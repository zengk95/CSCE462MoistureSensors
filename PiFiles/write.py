#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2014, Oscar Acena <oscaracena@gmail.com>
# This software is under the terms of Apache License v2 or later.

from __future__ import print_function

import sys, os
from gattlib import GATTRequester


class Reader(object):
    def __init__(self, address):
        try:
            self.requester = GATTRequester(address, False)
            self.connect()
            if self.requester.is_connected():
                self.send_data()
                sys.stdout.flush()
                self.requester.disconnect()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def connect(self):
        print("Connecting...", end=' ')
        sys.stdout.flush()

        self.requester.connect(True)
        print("OK!")

    def send_data(self):
        #test123 = self.requester.read_by_handle(0x25)[0]
        #print(test123)
        #send = ['t', 'r', 'i']
        self.requester.write_by_handle(0x25, "OK")

        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <addr>".format(sys.argv[0]))
        sys.exit(1)

    Reader(sys.argv[1])
    print("Done.")

