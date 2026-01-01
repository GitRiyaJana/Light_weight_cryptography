#!/usr/bin/env python3
# =============================================
# 12-Round Gimli-style permutation
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

def small_swap(x, y, z):
    """Swaps columns 0 and 1, and columns 2 and 3."""
    x = [x[1], x[0], x[3], x[2]]
    y = [y[1], y[0], y[3], y[2]]
    z = [z[1], z[0], z[3], z[2]]
    return x, y, z

def big_swap(x, y, z):
    """Swaps columns 0 and 2, and columns 1 and 3."""
    x = [x[2], x[3], x[0], x[1]]
    y = [y[2], y[3], y[0], y[1]]
    z = [z[2], z[3], z[0], z[1]]
    return x, y, z

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
# Encryption (12 rounds)
# ---------------------------
def gimli_encrypt(state, rounds=tuple(range(12, 0, -1)), verbose=False):
    x, y, z = state
    if verbose:
        print_state(x, y, z, "Initial state")

    for r in rounds:
        if verbose:
            print(f"\n=== Round {r} (Encryption) ===")

        x, y, z = rotate_planes(x, y, z)
        if verbose:
            print_state(x, y, z, "After rotation")

        x, y, z = sbox_lanes(x, y, z)
        if verbose:
            print_state(x, y, z, "After S-box layer")

        if r % 4 == 0:
            x, y, z = small_swap(x, y, z)
            if verbose:
                print("Applied small swap (columns)")
        elif r % 4 == 2:
            x, y, z = big_swap(x, y, z)
            if verbose:
                print("Applied big swap (columns)")
        if verbose:
            print_state(x, y, z, "After swap")

        x = add_round_constant(x, r)
        if verbose:
            print_state(x, y, z, "After round constant")

    if verbose:
        print("\n=== Final encrypted state ===")
        print_state(x, y, z, "Ciphertext")
    return x, y, z

# ---------------------------
# Decryption (inverse)
# ---------------------------
def gimli_decrypt(state, rounds=tuple(range(12, 0, -1)), verbose=False):
    x, y, z = state
    if verbose:
        print_state(x, y, z, "Initial ciphertext state")

    for r in reversed(rounds):
        if verbose:
            print(f"\n=== Round {r} (Decryption) ===")

        x = remove_round_constant(x, r)
        if verbose:
            print_state(x, y, z, "After removing round constant")

        if r % 4 == 0:
            x, y, z = small_swap(x, y, z)
            if verbose:
                print("Reversed small swap (columns)")
        elif r % 4 == 2:
            x, y, z = big_swap(x, y, z)
            if verbose:
                print("Reversed big swap (columns)")
        if verbose:
            print_state(x, y, z, "After undoing swap")

        x, y, z = inv_sbox_lanes(x, y, z)
        if verbose:
            print_state(x, y, z, "After inverse S-box")

        x, y, z = inv_rotate_planes(x, y, z)
        if verbose:
            print_state(x, y, z, "After inverse rotation")

    if verbose:
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
    enc_state = gimli_encrypt(state, verbose=True)

    print("\n\n=== DECRYPTION ===")
    dec_state = gimli_decrypt(enc_state, verbose=True)
