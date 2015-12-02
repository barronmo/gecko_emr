"""
Created on Sat Apr 27 2013

This provides the timestamping service as a WSGI app.

@author: Brian Visel <eode@eptitude.net>
"""

import os

import bottle
from bottle import get, put, post, request, response  # route, run

import config
import exception
from stamp import TimeStampInterface


DEBUG = True

interface = TimeStampInterface(config.algorithm, config.policy,
                               os.path.sep.join([config.data_dir,
                                                 config.config]),
                               config.signer, config.passin, config.inkey,
                               config.chain, config.use_token)


@get('/')
def index_get():
    return "Timestamp Server"


#@route('/', method='PUT')
@put('/')
def index_put():
    return request.body.read()


@post('/')
def index_post():
    try:
        response.content_type = 'application/timestamp-reply'
        return interface.stamp_request(request.body.read())
    except exception.OpenSSLError as e:
        return '\n'.join([e.stdout.decode('utf-8'), e.stderr.decode('utf-8'),
                          str(e.command)])

#run(host='timestamp', port=8080, server='gunicorn',
#    workers=4, log_syslog=True)

app = bottle.default_app()

# Debugging..
bottle.debug(DEBUG)
app.catchall = False

if __name__ == "__main__":
    app.run()