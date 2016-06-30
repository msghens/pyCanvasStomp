#!/usr/bin/env python2

import base64,zlib

from getpass import getpass



zd_b64d = lambda s: zlib.decompress(base64.decodestring(s))

zd_b64e = lambda s: base64.encodestring(zlib.compress(s))


tobe = raw_input("Enter string to encode: ")

encoded_str = zd_b64e(tobe)

print "Encoded string: " + encoded_str
print "Decoded string: " + zd_b64d(encoded_str)
