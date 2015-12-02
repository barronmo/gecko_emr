# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 18:44:54 2013

Configuration for timestamp server.  All options must be present, even if set
to None.

Members follow capitalization of their namesake OpenSSL options.

@author: Brian Visel <eode@eptitude.net>
"""
import os


### Configuration ###

data_dir = '/opt/ts_server'

### OpenSSL options
## ts client and server options
# config
# OpenSSL Configuration File - expected to be in the data dir
config = 'ssl/openssl.cnf'

# policy
# This depends on the config file selected and what policies are defined there.
# client: Defines the policy the server should use in its response.
# server: Defines the default policy to use for the response unless the client
# explicitly requires a particular TSA policy.
# both: The OID can be specified either in dotted notation or with its name.
# Overrides the default_policy config file option. (Optional)
policy = None

# use_token
# This will cause the client to use 'token_in' and the server to use
# 'token_out'.  Tokens are a different timestamp format.  It is important
# that this remain consistent across the same implementation.
use_token = True

## ts client options
# algorithm
# this may be any of the following:
# 'md4', 'md5', 'mdc2', 'ripemd160', 'sha', 'sha1', 'sha224', 'sha256',
# 'sha384', 'sha512', 'whirlpool'
# Sha 512 and whirlpool are the strongest.
algorithm = 'sha512'

# untrusted
# This is the path to a file which has the untrusted certificates required to
# complete the certificate chain -- namely, the TSA Signing Cert.
untrusted = data_dir + os.path.sep + 'ssl/certs/ts_server_cert.pem'

# CAfile
# This is the path to a file which has the trusted certificates required to
# complete the certificate chain -- namely, the certificate authority or
# authorities which were involved in signing the TSA Signing Cert.
CAfile = data_dir + os.path.sep + 'ssl/certs/ts_server_authority_cert.pem'

# CApath
# Optionally, if there are multiple certs which must be checked and aggregating
# them into one file is inconvenient, then you can use CApath.  However,
# ensure you run c_rehash from the CApath folder if you do, or certificates
# will not be recognized.
CApath = None

## ts server options
# signer
# The location of the signer certificate of the TSA in PEM format. The TSA
# signing certificate must have exactly one extended key usage assigned to it:
# timeStamping. The extended key usage must also be critical, otherwise the
# certificate is going to be refused. Overrides the signer_cert variable of
# the OpenSSL config file. (Optional)
signer = None

# passin
# Specifies the password source for the private key of the TSA. See
# OpenSSL documentation on PASS PHRASE ARGUMENTS in openssl(1). (Optional)
passin = 'pass:blah'

# inkey
# The signer private key of the TSA in PEM format. Overrides the signer_key
# config file option. (Optional)
inkey = None

# chain
# The collection of certificates in PEM format that will all be included in
# the response in addition to the signer certificate if the -cert option was
# used for the request. This file is supposed to contain the certificate chain
# for the signer certificate from its issuer upwards.
# The certificate chain is not built automatically. (Optional)
chain = None

