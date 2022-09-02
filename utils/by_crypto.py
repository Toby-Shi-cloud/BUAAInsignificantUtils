import re
import rsa
import random
import base64
import string
from hashlib import sha1, md5
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding


def md5_sign(data):
    return md5(data).hexdigest()


def sha1_sign(data):
    return sha1(data).hexdigest()


def create_rsa_key(text):
    match = re.search('RSA_PUBLIC_KEY="(.+?)"', text)
    if match.group(1):
        key = ['-----BEGIN PUBLIC KEY-----', match.group(1), '-----END PUBLIC KEY-----']
        return rsa.PublicKey.load_pkcs1_openssl_pem('\n'.join(key).encode())
    else:
        print('error: rsa public key not found')
        exit(0)


def rsa_encode(key, data):
    return base64.b64encode(rsa.encrypt(data, key))


def create_aes_key(key, assign=None):
    if assign is None:
        aes_key = ''.join(random.sample(string.ascii_letters + string.digits, 16)).encode()
    else:
        aes_key = assign
    cipher = AES.new(aes_key, AES.MODE_ECB)
    aes_key = base64.b64encode(rsa.encrypt(aes_key, key))
    return aes_key, cipher


def aes_encode(cipher, data):
    fix = padding.PKCS7(128).padder()
    data = fix.update(data) + fix.finalize()
    return cipher.encrypt(data)


def aes_decode(cipher, data):
    fix = padding.PKCS7(128).unpadder()
    data = cipher.decrypt(data)
    return fix.update(data) + fix.finalize()
