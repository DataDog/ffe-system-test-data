"""Deterministic dependency flag-key encryption for precomputed fixtures."""

import base64
import hashlib
import hmac

AAD = b"datadog.feature-flags.dependency-key.v1\0"
INFO = b"datadog.feature-flags.dependency-key.v1"
ENCRYPTION_INFO = INFO + b"\0enc"
NONCE_KEY_INFO = INFO + b"\0nonce"
NONCE_DOMAIN = b"datadog.feature-flags.dependency-key.nonce.v1\0"


def encrypt(root_key, dependency_key, salt):
    extracted = hmac.new(salt, root_key.encode(), hashlib.sha256).digest()
    encryption_key = _hkdf_expand(extracted, ENCRYPTION_INFO)
    nonce_key = _hkdf_expand(extracted, NONCE_KEY_INFO)
    plaintext = dependency_key.encode()
    nonce = hmac.new(nonce_key, NONCE_DOMAIN + plaintext, hashlib.sha256).digest()[:12]
    expanded = _expand_key(encryption_key)
    j0 = nonce + b"\0\0\0\1"
    ciphertext = _ctr(expanded, j0, plaintext)
    lengths = (len(AAD) * 8).to_bytes(8, "big") + (len(ciphertext) * 8).to_bytes(
        8, "big"
    )
    authentication = _ghash(
        _pad(AAD) + _pad(ciphertext) + lengths,
        int.from_bytes(_aes(expanded, bytes(16)), "big"),
    )
    tag = bytes(
        a ^ b for a, b in zip(_aes(expanded, j0), authentication.to_bytes(16, "big"))
    )
    return base64.urlsafe_b64encode(nonce + ciphertext + tag).rstrip(b"=").decode()


def _hkdf_expand(extracted, info):
    return hmac.new(extracted, info + b"\1", hashlib.sha256).digest()


def _expand_key(key):
    words = [
        int.from_bytes(key[offset : offset + 4], "big") for offset in range(0, 32, 4)
    ]
    rcon = 1
    for index in range(8, 60):
        value = words[index - 1]
        if index % 8 == 0:
            value = _sub_word(_rotate_word(value)) ^ (rcon << 24)
            rcon = _multiply(rcon, 2)
        elif index % 8 == 4:
            value = _sub_word(value)
        words.append(words[index - 8] ^ value)
    return words


def _aes(words, block):
    state = list(block)
    _add_round_key(state, words, 0)
    for round_number in range(1, 15):
        state[:] = [_sbox(value) for value in state]
        state[:] = [
            state[0],
            state[5],
            state[10],
            state[15],
            state[4],
            state[9],
            state[14],
            state[3],
            state[8],
            state[13],
            state[2],
            state[7],
            state[12],
            state[1],
            state[6],
            state[11],
        ]
        if round_number != 14:
            for column in range(4):
                offset = column * 4
                a, b, c, d = state[offset : offset + 4]
                state[offset : offset + 4] = [
                    _multiply(a, 2) ^ _multiply(b, 3) ^ c ^ d,
                    a ^ _multiply(b, 2) ^ _multiply(c, 3) ^ d,
                    a ^ b ^ _multiply(c, 2) ^ _multiply(d, 3),
                    _multiply(a, 3) ^ b ^ c ^ _multiply(d, 2),
                ]
        _add_round_key(state, words, round_number)
    return bytes(state)


def _add_round_key(state, words, round_number):
    for column in range(4):
        word = words[round_number * 4 + column]
        for row in range(4):
            state[column * 4 + row] ^= (word >> (24 - row * 8)) & 0xFF


def _ctr(words, j0, plaintext):
    counter = int.from_bytes(j0, "big")
    result = bytearray()
    for offset in range(0, len(plaintext), 16):
        counter = (counter & ~0xFFFFFFFF) | ((counter + 1) & 0xFFFFFFFF)
        stream = _aes(words, counter.to_bytes(16, "big"))
        result.extend(a ^ b for a, b in zip(plaintext[offset : offset + 16], stream))
    return bytes(result)


def _ghash(data, hash_key):
    result = 0
    for offset in range(0, len(data), 16):
        result = _galois_multiply(
            result ^ int.from_bytes(data[offset : offset + 16], "big"), hash_key
        )
    return result


def _galois_multiply(left, right):
    result = 0
    value = right
    for bit in range(128):
        if left & (1 << (127 - bit)):
            result ^= value
        value = (value >> 1) ^ (0xE1000000000000000000000000000000 if value & 1 else 0)
    return result


def _pad(value):
    return value + bytes((-len(value)) % 16)


def _rotate_word(value):
    return ((value << 8) & 0xFFFFFFFF) | (value >> 24)


def _sub_word(value):
    return sum(_sbox((value >> shift) & 0xFF) << shift for shift in (24, 16, 8, 0))


def _sbox(value):
    inverse = _power(value, 254) if value else 0
    return (
        inverse
        ^ _rotate_byte(inverse, 1)
        ^ _rotate_byte(inverse, 2)
        ^ _rotate_byte(inverse, 3)
        ^ _rotate_byte(inverse, 4)
        ^ 0x63
    )


def _rotate_byte(value, count):
    return ((value << count) | (value >> (8 - count))) & 0xFF


def _power(value, exponent):
    result = 1
    while exponent:
        if exponent & 1:
            result = _multiply(result, value)
        value = _multiply(value, value)
        exponent >>= 1
    return result


def _multiply(left, right):
    result = 0
    while right:
        if right & 1:
            result ^= left
        left = ((left << 1) ^ (0x11B if left & 0x80 else 0)) & 0xFF
        right >>= 1
    return result
