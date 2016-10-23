#!/usr/bin/env python
# coding=utf-8

import os
import random
import ctypes

try:
    import requests
except ImportError:
    print 'You need to install requests to use full functions.'

import consts

__all__ = ['CETCipher', 'CETTypes', 'CETConfig', 'CETTicket']


def random_mac():
    return '-'.join(['%.2X' % random.randint(0, 16) for _ in xrange(6)])


DES_cblock = ctypes.c_char * 8
DES_LONG = ctypes.c_int


class TicketNotFound(Exception):
    pass


class ks(ctypes.Union):
    _fields_ = [('cblock', DES_cblock), ('deslong', DES_LONG * 2)]


class DES_key_schedule(ctypes.Structure):
    _fields_ = [('ks', ks * 16), ]


class CETCipher(object):
    DECRYPT = 0
    ENCRYPT = 1

    @staticmethod
    def check_des_key(key):
        if len(key) != 8:
            raise ValueError("DES key should be 8 characters")

    def __init__(self, ticket_number_key, request_data_key,
                 libcrypto_path=None):
        self.check_des_key(ticket_number_key)
        self.check_des_key(request_data_key)

        self.ticket_number_key = ticket_number_key
        self.request_data_key = request_data_key

        if not libcrypto_path:
            from ctypes.util import find_library
            libcrypto_path = find_library('crypto')
            if not libcrypto_path:
                raise Exception('libcrypto(OpenSSL) not found')

        self.libcrypto = ctypes.CDLL(libcrypto_path)

        if hasattr(self.libcrypto, 'OpenSSL_add_all_ciphers'):
            self.libcrypto.OpenSSL_add_all_ciphers()

    def process_data(self, indata, key, is_enc=True):
        is_enc = self.ENCRYPT if is_enc else self.DECRYPT
        length = len(indata)

        indata = ctypes.create_string_buffer(indata, length)
        outdata = ctypes.create_string_buffer(length)
        n = c_int(0)
        key = DES_cblock(*tuple(key))
        key_schedule = DES_key_schedule()
        self.libcrypto.DES_set_odd_parity(key)
        self.libcrypto.DES_set_key_checked(
            ctypes.byref(key), ctypes.byref(key_schedule))

        self.libcrypto.DES_cfb64_encrypt(
            ctypes.byref(indata), ctypes.byref(outdata), ctypes.c_int(length),
            ctypes.byref(key_schedule), ctypes.byref(key), ctypes.byref(n),
            ctypes.c_int(is_enc))

        return outdata.raw

    def decrypt_ticket_number(self, ciphertext):
        ciphertext = ciphertext[2:]
        return self.process_data(
            ciphertext, self.ticket_number_key, is_enc=False)

    def encrypt_ticket_number(self, ticket_number):
        ciphertext = self.process_data(
            ticket_number, self.ticket_number_key, is_enc=True)
        ciphertext = '\x35\x2c' + ciphertext
        return ciphertext

    def decrypt_request_data(self, ciphertext):
        return self.process_data(
            ciphertext, self.request_data_key, is_enc=False)

    def encrypt_request_data(self, request_data):
        return self.process_data(
            request_data, self.request_data_key, is_enc=True)


class CETTypes(object):
    CET4 = 1
    CET6 = 2


class CETConfig(object):
    SEARCH_URL = consts.SEARCH_URL
    SCORE_URL = consts.SCORE_URL
    PROVINCES = consts.PROVINCES

    @classmethod
    def province_id(cls, province):
        if province not in cls.PROVINCES:
            raise KeyError("this province %s not supported" % province)
        return cls.PROVINCES[province]

    @staticmethod
    def user_agent():
        return '西木野真姬'


class CETTicket(object):
    """
        usage:
        ct = CETTicket()
        print ct.find_ticket_number(u'浙江', u'浙江海洋学院', u'XXX', cet_type=2)
    """

    def __init__(self, cipher):
        self.cipher = cipher

    def find_ticket_number(self,
                           province,
                           school,
                           name,
                           examroom='',
                           cet_type=CETTypes.CET4):
        """
            You can read the `school.json` file to check if your school is supported.
            cet_type:
                    1 ==> cet4
                    2 ==> cet6
        """

        province_id = CETConfig.province_id(province)
        param_data = u'type=%d&provice=%d&school=%s&name=%s&examroom=%s&m=%s' % (
            cet_type, province_id, school, name, examroom, random_mac())
        param_data = param_data.encode('gbk')
        encrypted_data = self.cipher.encrypt_request_data(param_data)

        resp = requests.post(
            url=CETConfig.SEARCH_URL,
            data=encrypted_data,
            headers={'User-Agent': CETConfig.user_agent()})
        ticket_number = self.cipher.decrypt_ticket_number(resp.content)
        if ticket_number == '':
            raise TicketNotFound('Cannot find ticket number.')

        return ticket_number


if __name__ == '__main__':
    pass
