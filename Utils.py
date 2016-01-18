import hashlib
import math


class Cipher(object):
    def __init__(self, key):
        self.key = self.normalize_key(key)

    def decrypt(self, message):
        return ''.join([self.decrypt_character(char, self.key) for char in message])

    @staticmethod
    def decrypt_character(char, key):
        return chr((ord(char) - key + 256) % 256)

    def encrypt(self, message):
        return ''.join([self.encode_character(char, self.key) for char in str(message)])

    @staticmethod
    def encode_character(char, key):
        return chr((ord(char) + key) % 256)

    @staticmethod
    def normalize_key(key):
        if isinstance(key, str):
            return sum([ord(c) for c in key])
        return key


def hash_function(m):
    return hashlib.md5(m).hexdigest()


# def hash_function(m):
#     result = 17
#     a = 0.1731
#     maximum = 41930113
#     for char in m:
#         result += hash_integer(ord(char), a, maximum)
#     final = str(hash_integer(result, a, maximum))
#     intended = len(str(maximum))
#     return '0' * (intended - len(final)) + final


# def hash_integer(integer, a, m):
#     return int(math.floor((integer * a % 1) * m))


def hash_n_times(content, times):
    for _ in range(times):
        content = hash_function(content)
    return content
