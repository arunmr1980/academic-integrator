import os
import binascii
import datetime

def generate_key(length):
    key = os.urandom (length)
    return binascii.hexlify (key).decode ('ascii')
