# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 20:01:55 2013

@author: Brian Visel <eode@eptitude.net>
"""
import os

import requests

import config
from exception import OpenSSLError, ConfigurationError
from stamp import TimeStampInterface


class TimeStampClient(object):
    def __init__(self, server_address):
        """TimeStampClient(server_address) -> timestamping client"""
        self.address = server_address
        self._interface = TimeStampInterface(config.algorithm, config.policy,
                                             os.path.sep.join([config.data_dir,
                                                               config.config]),
                                             use_token=config.use_token,
                                             ca_file=config.CAfile,
                                             ca_path=config.CApath,
                                             untrusted=config.untrusted)

    def stamp(self, data):
        """stamp(data) -> dict
        Stamp the string 'data', returning a dict with items:
            code    - Error code from OpenSSL
            reason  - Explanation of status, usually from OpenSSL
            stamp   - Stamp to store in the database
            status  - Status as returned from OpenSSL
            success - a True/False value for easy success checking
        When an error occurs, the dict also contains the following item:
            command - The exact OpenSSL command which failed
        When success occurs, the dict also contains the following item:
            utctime - a datetime object with the date and time

        In order to verify timestamp, you need:
            the original data
            result['stamp']
          Since you already have the original data, the only thing you
          technically need to store is the stamp.
        """
        request = self._interface.generate_request(data)
        response = requests.post(self.address, request)
        validation = self.check(data, response.content)
        validation['stamp'] = response.content
        if not validation['status']:
            validation['status'] = 'Error'
        if validation['success']:
            token = self._interface.read_stamp(validation['stamp'], text=False)
            datetime = self._interface.parse_date(token)
            validation['utctime'] = datetime
        return validation

    def check(self, data, stamp):
        """check(data, stamp) -> dict
        ..the dict contains the items:
            code    - Error code from OpenSSL
            reason  - Explanation of status, usually from OpenSSL
            status  - Status as returned from OpenSSL
            success - a True/False value for easy success checking
        ..and on failure, it also includes:
            command - The exact OpenSSL command which failed
        """
        return self._interface.verify_stamp(data, stamp)

    def read(self, stamp):
        """check(stamp) -> dict
        ..the dict contains the items:
            text - The full data of the stamp in human-readable form
            utctime - a python date object of the time of the stamp
        """
        text = self._interface.read_stamp(stamp)
        token = self._interface.read_stamp(stamp, text=False)
        datetime = self._interface.parse_date(token)
        return {'text': text, 'utctime': datetime}
