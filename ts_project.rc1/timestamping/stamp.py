# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 15:05:42 2013

This handles the actual interactions with Open SSL.

@author: Brian Visel <eode@eptitude.net>
"""
from datetime import datetime
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE

from exception import OpenSSLError, ConfigurationError


class TimeStampInterface(object):
    """This is a wrapper around OpenSSL's Time Stamping Authority tools.
    For now, it is an incomplete implementation which includes only the parts
    I need, unless someone requests or submits further work on it."""
    _algo = {'md4', 'md5', 'mdc2', 'ripemd160', 'sha', 'sha1', 'sha224',
             'sha256', 'sha384', 'sha512', 'whirlpool'
             }

    def __init__(self, algorithm='sha512', policy=None, config=None,
                 signer=None, passin=None, inkey=None, chain=None,
                 use_token=None, ca_file=None, ca_path=None, untrusted=None):
        """TimeStampInterface(alg, policy, conf, signer, passin, key, chain)
        -> TimeStampInterface object
        No arguments required for client.

        algorithm := one of 'md4', 'md5', 'mdc2', 'ripemd160', 'sha', 'sha1',
                     'sha224', 'sha256', 'sha384', 'sha512', 'whirlpool', or
                     None.  Defaults to 'sha512'.
        policy := A named policy, defined in config, default None
        config := OpenSSL configuration file to use, default None
        signer := Path to signing cert to use
        passin := one of 'pass:password', 'env:var', 'file:pathname',
                  'fd:number', 'stdin', or None.  Defaults to None.
        inkey := Path to the signer private key of the TSA in PEM format.
                 Overrides the signer_key config file option.
        chain := Path to certificate chain file to send upon client request
        use_token := client and server -- use token format
        ca_file := trusted certificate authorities needed to verify (file)
        ca_path := trusted certificate authorities needed to verify (folder)
            Note that only one of ca_file and ca_path may be set.
            Also Note that running c_rehash on the ca_path may be necessary.
        untrusted := Untrusted certificates necessary for chain completion
            The TSA cert itself, for example, is an untrusted cert.

        Typical client usage:
            TimeStampInterface('sha256', config='/some/openssl.cnf',
                               use_token=True, ca_file='/data/ts_ca_cert.pem',
                               untrusted='/data/ts_cert.pem')
        """
        if not algorithm in self._algo:
            raise ValueError("Algorithm must be one of: " + str(self._algo))
        self.algorithm = algorithm
        self.policy = policy
        self.config = config
        self.signer = signer
        self.passin = passin
        self.inkey = inkey
        self.chain = chain
        self.use_token = use_token
        self.untrusted = untrusted
        self.CAfile = ca_file
        self.CApath = ca_path

        self.human = False
        self.authority_cert = None

    permitted_algorithms = property(lambda self: set(self._algo))

    def generate_request(self, data):
        openssl_command = ['openssl', 'ts', '-query', '-no_nonce',
                           '-' + self.algorithm,
                           ]
        if self.policy:
            openssl_command.extend(['-policy', self.policy])
#        if not self.authority_cert:
#            openssl_command.append('-cert')
        if self.human:
            openssl_command.append('-text')
        if self.config:
            openssl_command.extend(['-config', self.config])
        openssl = Popen(openssl_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        openssl.stdin.write(data)
        openssl.stdin.close()
        error = openssl.wait()
        if error:
            stdout = openssl.stdout.read()
            stderr = openssl.stderr.read()
            msg = "Received error code {} while generating request"
            err = OpenSSLError(msg.format(error), data, stdout, stderr)
            err.data = data
            err.out = stdout
            err.err = stderr
            print(stdout)
            print(stderr)
            raise err
        return openssl.stdout.read()

    def stamp_request(self, request):
        openssl_command = ['openssl', 'ts', '-reply']
        if self.use_token:
            openssl_command.append('-token_out')
        if self.human:
            openssl_command.append('-text')
        options = ['policy', 'config', 'signer', 'inkey', 'chain', 'passin']
        for option in options:
            if getattr(self, option):
                openssl_command.extend(['-' + option, getattr(self, option)])
        openssl_command.extend(['-queryfile', '/dev/stdin',
                                '-out', '/dev/stdout'])
        openssl = Popen(openssl_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        openssl.stdin.write(request)
        openssl.stdin.close()
        error = openssl.wait()
        if error:
            msg = "Received error code {} while signing data"
            err = OpenSSLError(msg.format(error), request)
            err.data = request
            err.stdout = openssl.stdout.read()
            err.stderr = openssl.stderr.read()
            err.command = openssl_command
            raise err
        return openssl.stdout.read()

    def verify_stamp(self, data, stamp):
        openssl_command = ['openssl', 'ts', '-verify']
        if self.use_token:
            openssl_command.append('-token_in')
        if self.human:
            openssl_command.append('-text')
        if (self.CAfile and self.CApath) \
          or (not self.CAfile and not self.CApath):
            msg = "Must have one and only one of CAfile and CApath"
            raise ConfigurationError(msg)
        if not self.untrusted:
            raise ConfigurationError("'untrusted' is not set.")
        options = ['config', 'CAfile', 'CApath', 'untrusted', ]
        for option in options:
            if getattr(self, option):
                openssl_command.extend(['-' + option, getattr(self, option)])
        openssl_command.extend(['-data', '/dev/stdin'])
        temp = NamedTemporaryFile()
        temp.write(stamp)
        temp.flush()
        temp.seek(0)
        openssl_command.extend(['-in', temp.name])
        openssl = Popen(openssl_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        openssl.stdin.write(data)
        openssl.stdin.close()
        error = openssl.wait()
        stderr = openssl.stderr.read()
        stdout = openssl.stdout.read()
        if not error:
            return {'code': error, 'reason': 'Matched', 'success': True,
                    'status': stdout}
        return {'code': error, 'reason': stderr, 'success': False,
                'status': stdout, 'command': openssl_command}

    def read_stamp(self, stamp, text=True):
        """read_stamp(stamp) -> token_data in text format
        read_stamp(stamp, text=False) -> token data
        """
        openssl_command = ['openssl', 'ts', '-reply', '-token_out']
        if self.use_token:
            openssl_command.append('-token_in')
        if text:
            openssl_command.append('-text')
        openssl_command.extend(['-in', '/dev/stdin'])
        openssl = Popen(openssl_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        openssl.stdin.write(stamp)
        openssl.stdin.close()
        error = openssl.wait()
        if not error:
            return openssl.stdout.read()
        msg = "Received error code {} while trying to read stamp"
        err = OpenSSLError(msg.format(error), stamp)
        err.stdout = openssl.stdout.read()
        err.stderr = openssl.stderr.read()
        err.command = openssl_command
        err.data = stamp
        raise err

    def parse_date(self, der):
        openssl_command = ['openssl', 'asn1parse', '-inform', 'DER']
        openssl = Popen(openssl_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        openssl.stdin.write(der)
        openssl.stdin.close()
        error = openssl.wait()
        if error:
            return None
        data = openssl.stdout.read()
        needle = "prim: UTCTIME"
        start = data.find(needle) + len(needle)
        end = data.find('\n', start)
        time = data[start:end].strip().split()[-1]
        return datetime.strptime(time, ':%y%m%d%H%M%SZ')

