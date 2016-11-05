import unittest

from libcet import cet


class TestEncrypt(unittest.TestCase):
    def setUp(self):
        self.crypter = cet.CETCrypter('021yO6d<', 'QghdW;O;')

    def test_encrypt(self):
        plaintext = '123456789'
        self.assertEqual(
            plaintext,
            self.crypter.decrypt_ticket_number(self.crypter.encrypt_ticket_number(plaintext)))
        self.assertEqual(
            plaintext,
            self.crypter.decrypt_request_data(self.crypter.encrypt_request_data(plaintext)))
