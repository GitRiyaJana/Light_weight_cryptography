#!/usr/bin/env python3
# =============================================
# 2-Round Gimli-style permutation (Corrected Swap)
# Encryption + Decryption
# with 3-bit S-box [7, 4, 6, 1, 0, 5, 2, 3]
# =============================================

ROUND_CONSTANT = 0x9e377900

def rotl32(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xffffffff

def rotr32(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xffffffff

# ---------------------------
# 3-bit S-box and its inverse
# ---------------------------
SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
INV_SBOX = [SBOX.index(i) for i in range(8)]

def sbox_lanes(x, y, z):
    new_x, new_y, new_z = [], [], []
    for xi, yi, zi in zip(x, y, z):
        sx = sy = sz = 0
        for bit in range(32):
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
        for bit in range(32):
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
# Rotations and swaps (Corrected)
# ---------------------------
def rotate_planes(x, y, z):
    return ([rotl32(w, 24) for w in x],
            [rotl32(w, 9)  for w in y],
            z)

def inv_rotate_planes(x, y, z):
    return ([rotr32(w, 24) for w in x],
            [rotr32(w, 9)  for w in y],
            z)

def small_swap(x, y, z):
    x[0], x[1] = x[1], x[0]
    x[2], x[3] = x[3], x[2]
    y[0], y[1] = y[1], y[0]
    y[2], y[3] = y[3], y[2]
    z[0], z[1] = z[1], z[0]
    z[2], z[3] = z[3], z[2]
    return x, y, z

def big_swap(x, y, z):
    x[0], x[2] = x[2], x[0]
    x[1], x[3] = x[3], x[1]
    y[0], y[2] = y[2], y[0]
    y[1], y[3] = y[3], y[1]
    z[0], z[2] = z[2], z[0]
    z[1], z[3] = z[3], z[1]
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
    print("x:", " ".join(format(w, "032b") for w in x))
    print("y:", " ".join(format(w, "032b") for w in y))
    print("z:", " ".join(format(w, "032b") for w in z))

# ---------------------------
# Encryption
# ---------------------------
def gimli_encrypt(state, num_rounds=24):
    rounds = [24 - i for i in range(num_rounds)]
    x, y, z = state
    
    for r in rounds:
        print(f"\n--- Round {r} ---")
        x, y, z = rotate_planes(x, y, z)
        x, y, z = sbox_lanes(x, y, z)
        if r % 4 == 0:
            x, y, z = small_swap(x, y, z)
        elif r % 4 == 2:
            x, y, z = big_swap(x, y, z)
        x = add_round_constant(x, r)
        print_state(x, y, z, label=f"State after round {r}")
        
    return x, y, z

# ---------------------------
# Decryption (inverse)
# ---------------------------
def gimli_decrypt(state, num_rounds=2):
    rounds = [24 - i for i in range(num_rounds)]
    x, y, z = state

    for r in reversed(rounds):
        x = remove_round_constant(x, r)
        if r % 4 == 0:
            x, y, z = small_swap(x, y, z)
        elif r % 4 == 2:
            x, y, z = big_swap(x, y, z)
        x, y, z = inv_sbox_lanes(x, y, z)
        x, y, z = inv_rotate_planes(x, y, z)

    return x, y, z

# ---------------------------
# Differential Analysis
# ---------------------------
def run_differential_analysis():
    # First propagation (rounds 24 to 22)
    print("=== First Propagation (Rounds 24 to 22) ===")
    
    # Initial states with a single-bit difference
    state1 = (
        [0x00000001, 0x00000000, 0x00000000, 0x00000000],
        [0x00000000, 0x00000000, 0x00000000, 0x00000000],
        [0x00000000, 0x00000000, 0x00000000, 0x00000000]
    )
    state2 = (
        [0x00000000, 0x00000000, 0x00000000, 0x00000000],
        [0x00000000, 0x00000000, 0x00000000, 0x00000000],
        [0x00000000, 0x00000000, 0x00000000, 0x00000000]
    )

    # Run for 3 rounds (24, 23, 22)
    enc_state1_22 = gimli_encrypt(state1, num_rounds=3)
    enc_state2_22 = gimli_encrypt(state2, num_rounds=3)

    # Calculate and print the difference trail
    diff_22 = [s1 ^ s2 for s1, s2 in zip(enc_state1_22[0] + enc_state1_22[1] + enc_state1_22[2], 
                                        enc_state2_22[0] + enc_state2_22[1] + enc_state2_22[2])]
    print("Difference after round 22:")
    print_state(diff_22[0:4], diff_22[4:8], diff_22[8:12])

    # Second propagation (rounds 20 to 22)
    print("\n=== Second Propagation (Rounds 20 to 22) ===")
    
    # Base state
    base_state = (
        [0x12345678, 0x9abcdef0, 0xfedcba98, 0x76543210],
        [0xdeadbeef, 0xcafebabe, 0xfeedface, 0xfacefeed],
        [0xaaaaaaaa, 0xbbbbbbbb, 0xcccccccc, 0xdddddddd]
    )

    # Run until round 20
    state_at_20 = gimli_encrypt(base_state, num_rounds=4)

    # Introduce a difference
    state_at_20_1 = state_at_20
    state_at_20_2 = (
        [state_at_20[0][0] ^ 0x1, state_at_20[0][1], state_at_20[0][2], state_at_20[0][3]],
        state_at_20[1],
        state_at_20[2]
    )

    # Run from round 20 to 22 (3 rounds)
    enc_state1_20_22 = gimli_encrypt(state_at_20_1, num_rounds=3)
    enc_state2_20_22 = gimli_encrypt(state_at_20_2, num_rounds=3)

    # Calculate and print the difference trail
    diff_20_22 = [s1 ^ s2 for s1, s2 in zip(enc_state1_20_22[0] + enc_state1_20_22[1] + enc_state1_20_22[2],
                                             enc_state2_20_22[0] + enc_state2_20_22[1] + enc_state2_20_22[2])]
    print("Difference after round 22 (starting from 20):")
    print_state(diff_20_22[0:4], diff_20_22[4:8], diff_20_22[8:12])

# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    run_differential_analysis()
