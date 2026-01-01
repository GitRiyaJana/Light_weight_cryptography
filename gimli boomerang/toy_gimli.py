#!/usr/bin/env python3
# =============================================
# 3-Round Gimli-style permutation
# Encryption + Decryption
# with 3-bit S-box [7, 4, 6, 1, 0, 5, 2, 3]
# =============================================

ROUND_CONSTANT = 0x9e

def rotl8(x, n):
    return ((x << n) | (x >> (8 - n))) & 0xff

def rotr8(x, n):
    return ((x >> n) | (x << (8 - n))) & 0xff

# ---------------------------
# 3-bit S-box and its inverse
# ---------------------------
SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
INV_SBOX = [SBOX.index(i) for i in range(8)]

def sbox_lanes(x, y, z):
    new_x, new_y, new_z = [], [], []
    for xi, yi, zi in zip(x, y, z):
        sx = sy = sz = 0
        for bit in range(8):
            a = (xi >> bit) & 1
            b = (yi >> bit) & 1
            c = (zi >> bit) & 1
            val = SBOX[(a << 2) | (b << 1) | c]
            sx |= ((val >> 2) & 1) << bit
            sy |= ((val >> 1) & 1) << bit
            sz |= (val & 1) << bit
        new_x.append(sx)
        new_y.append(sy)
        new_z.append(sz)
    return new_x, new_y, new_z

def inv_sbox_lanes(x, y, z):
    new_x, new_y, new_z = [], [], []
    for xi, yi, zi in zip(x, y, z):
        sx = sy = sz = 0
        for bit in range(8):
            a = (xi >> bit) & 1
            b = (yi >> bit) & 1
            c = (zi >> bit) & 1
            val = INV_SBOX[(a << 2) | (b << 1) | c]
            sx |= ((val >> 2) & 1) << bit
            sy |= ((val >> 1) & 1) << bit
            sz |= (val & 1) << bit
        new_x.append(sx)
        new_y.append(sy)
        new_z.append(sz)
    return new_x, new_y, new_z

# ---------------------------
# Rotations and swaps
# ---------------------------
def rotate_planes(x, y, z):
    return ([rotl8(w, 6) for w in x],
            [rotl8(w, 2)  for w in y],
            z)

def inv_rotate_planes(x, y, z):
    return ([rotr8(w, 6) for w in x],
            [rotr8(w, 2)  for w in y],
            z)

def small_swap(state):
    s = state[:]
    s[0], s[1] = s[1], s[0]
    s[2], s[3] = s[3], s[2]
    return s

def big_swap(state):
    s = state[:]
    s[0], s[2] = s[2], s[0]
    s[1], s[3] = s[3], s[1]
    return s

def add_round_constant(x, round_number):
    x = x[:]
    if round_number % 4 == 0:
        x[0] ^= (ROUND_CONSTANT ^ round_number)
    return x

def remove_round_constant(x, round_number):
    # XOR is its own inverse
    return add_round_constant(x, round_number)

# ---------------------------
# Bitwise matrix printer
# ---------------------------
def print_state(x, y, z, label="State"):
    print(f"\n{label} (3×4 bitwise matrix):")
    print("x:", " ".join(format(w, "08b") for w in x))
    print("y:", " ".join(format(w, "08b") for w in y))
    print("z:", " ".join(format(w, "08b") for w in z))

# ---------------------------
# Encryption (3 rounds)
# ---------------------------
def gimli_encrypt_3rounds(state, rounds=(24, 23, 22)):
    x, y, z = state
    print_state(x, y, z, "Initial state")

    for r in rounds:
        print(f"\n=== Round {r} (Encryption) ===")

        x, y, z = rotate_planes(x, y, z)
        print_state(x, y, z, "After rotation")

        x, y, z = sbox_lanes(x, y, z)
        print_state(x, y, z, "After S-box layer")

        combined = x + y + z
        if r % 4 == 0:
            combined = small_swap(combined)
            print("Applied small swap")
        elif r % 4 == 2:
            combined = big_swap(combined)
            print("Applied big swap")
        x, y, z = combined[0:4], combined[4:8], combined[8:12]
        print_state(x, y, z, "After swap")

        x = add_round_constant(x, r)
        print_state(x, y, z, "After round constant")

    print("\n=== Final encrypted state ===")
    print_state(x, y, z, "Ciphertext")
    return x, y, z

# ---------------------------
# Decryption (inverse)
# ---------------------------
def gimli_decrypt_3rounds(state, rounds=(24, 23, 22)):
    x, y, z = state
    print_state(x, y, z, "Initial ciphertext state")

    for r in reversed(rounds):
        print(f"\n=== Round {r} (Decryption) ===")

        x = remove_round_constant(x, r)
        print_state(x, y, z, "After removing round constant")

        combined = x + y + z
        if r % 4 == 0:
            combined = small_swap(combined)
            print("Reversed small swap")
        elif r % 4 == 2:
            combined = big_swap(combined)
            print("Reversed big swap")
        x, y, z = combined[0:4], combined[4:8], combined[8:12]
        print_state(x, y, z, "After undoing swap")

        x, y, z = inv_sbox_lanes(x, y, z)
        print_state(x, y, z, "After inverse S-box")

        x, y, z = inv_rotate_planes(x, y, z)
        print_state(x, y, z, "After inverse rotation")

    print("\n=== Final decrypted state ===")
    print_state(x, y, z, "Plaintext recovered")
    return x, y, z

# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    state = (
        [0x01, 0x00, 0x00, 0x00],
        [0x00, 0x00, 0x00, 0x00],
        [0x00, 0x00, 0x00, 0x00]
    )

    print("\n=== ENCRYPTION ===")
    enc_state = gimli_encrypt_3rounds(state)

    print("\n\n=== DECRYPTION ===")
    dec_state = gimli_decrypt_3rounds(enc_state)
