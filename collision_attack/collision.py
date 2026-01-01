#!/usr/bin/env python3
"""
Educational collision demo using the toy 12-round Gimli permutation.

IMPORTANT:
 - This is NOT an attack on real Gimli-Hash.
 - Output rate = 1 byte, rounds = 2 → collisions are trivial (birthday).
 - Demonstrates sponge hashing + collision search.
"""

import os
from Gimli_toy import gimli_encrypt   # <-- imports your toy permutation


# ==========================================================
#  Sponge-style toy hash (absorb ≤3 bytes, permute, squeeze)
# ==========================================================

def bytes_to_state(b):
    """
    Convert up to 3 message bytes into the Gimli state:
       (x,y,z) planes, 4 bytes each.

    Only x[0], y[0], z[0] are touched during absorption.
    """
    x = [0, 0, 0, 0]
    y = [0, 0, 0, 0]
    z = [0, 0, 0, 0]

    if len(b) >= 1: x[0] ^= b[0]
    if len(b) >= 2: y[0] ^= b[1]
    if len(b) >= 3: z[0] ^= b[2]
    return (x, y, z)


def toy_gimli_hash(msg: bytes, rounds=2) -> int:
    """
    EDUCATIONAL tiny Gimli hash:
       absorb → 2-round permutation → output 1 byte

    Hash value = x[0] & FF
    """
    # absorb into state
    state = bytes_to_state(msg)

    # run reduced permutation (R rounds)
    enc = gimli_encrypt(state, rounds=tuple(range(rounds, 0, -1)))

    # squeeze: output 1 byte from x-plane column 0
    x, y, z = enc
    return x[0] & 0xFF


# ==========================================================
#  Collision search (birthday style)
# ==========================================================

def collision_search(rounds=2):
    """
    Random search for two messages m1 != m2
    such that toy_gimli_hash(m1) == toy_gimli_hash(m2).
    """
    seen = {}
    attempts = 0

    while True:
        # pick a random short message (1–3 bytes)
        L = os.urandom(1)[0] % 3 + 1
        m = os.urandom(L)

        h = toy_gimli_hash(m, rounds)

        if h in seen and seen[h] != m:
            return seen[h], m, h, attempts

        seen[h] = m
        attempts += 1


# ==========================================================
#  Stand-alone execution
# ==========================================================

if __name__ == "__main__":
    m1, m2, h, tries = collision_search(rounds=2)

    print("======================================")
    print("EDUCATIONAL COLLISION FOUND")
    print("======================================")
    print(f"Total tries    : {tries}")
    print(f"Message 1 (hex): {m1.hex()}")
    print(f"Message 2 (hex): {m2.hex()}")
    print(f"Hash value     : {h:02x}")
    print("======================================")

