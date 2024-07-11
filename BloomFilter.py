import hashlib
import zlib
import mmh3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, size, hash_funcs):
        self.size = size
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)
        self.hash_funcs = hash_funcs

    def add(self, item):
        for f in self.hash_funcs:
            index = f(item) % self.size
            self.bit_array[index] = 1

    def contains(self, item):
        for f in self.hash_funcs:
            index = f(item) % self.size
            if not self.bit_array[index]:
                return False
        return True

    def count_bits(self):
        return self.bit_array.count()

# 定义hash函数
def hash_func_1(item):
    return int(hashlib.sha256(item.encode('utf-8')).hexdigest(), 16)

def hash_func_2(item):
    return int(hashlib.md5(item.encode('utf-8')).hexdigest(), 16)

def hash_func_sha1(item):
    return int(hashlib.sha1(item.encode('utf-8')).hexdigest(), 16)

def hash_func_crc32(item):
    return zlib.crc32(item.encode('utf-8'))

def hash_func_fnv1a(item):
    hash = 2166136261
    for c in item.encode('utf-8'):
        hash ^= c
        hash *= 16777619
    return hash

def hash_func_murmur(item):
    return mmh3.hash(item)