import copy

# ---------------------------
# Gimli permutation (4 rounds for demo)
# ---------------------------
def rotl32(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def gimli_permutation(state, rounds=4):
    s = state[:]
    for r in range(rounds, 0, -1):
        for col in range(4):
            x = rotl32(s[col], 24)
            y = rotl32(s[col+4], 9)
            z = s[col+8]

            s[col+8] = x ^ (z << 1 & 0xFFFFFFFF) ^ ((y & z) << 2 & 0xFFFFFFFF)
            s[col+4] = y ^ x ^ ((x | z) << 1 & 0xFFFFFFFF)
            s[col] = z ^ y ^ ((x & y) << 3 & 0xFFFFFFFF)

        if r & 3 == 0:
            s[0], s[1] = s[1], s[0]
            s[2], s[3] = s[3], s[2]
            s[0] ^= (0x9e377900 ^ r)
        if r & 3 == 2:
            s[0], s[2] = s[2], s[0]
            s[1], s[3] = s[3], s[1]

    return s

# ---------------------------
# Bit-basis for a byte
# ---------------------------
def byte_basis():
    return [1 << i for i in range(8)]

# ---------------------------
# Apply difference to one byte
# ---------------------------
def apply_diff_byte(state, word_index, byte_index, basis, subset):
    s = state[:]
    b = (s[word_index] >> (8*byte_index)) & 0xFF
    for i in range(len(basis)):
        if subset & (1 << i):
            b ^= basis[i]
    s[word_index] = (s[word_index] & ~(0xFF << (8*byte_index))) | (b << (8*byte_index))
    return s

# ---------------------------
# Compute t-th order derivative for a byte
# ---------------------------
def higher_order_derivative_byte(state, word_index, byte_index, order, rounds=4):
    basis = byte_basis()
    result = 0
    for subset in range(1 << order):
        s = apply_diff_byte(state, word_index, byte_index, basis, subset)
        s = gimli_permutation(s, rounds)
        b = (s[word_index] >> (8*byte_index)) & 0xFF
        # XOR according to alternating-sum formula
        if bin(subset).count("1") % 2 == 1:
            result ^= b
    return result

# ---------------------------
# Test derivatives for all bytes
# ---------------------------
def test_all_bytes():
    state = [0x00000001] + [0]*11
    print("Initial state:", [f"{x:08X}" for x in state])

    for word_index in range(12):
        for byte_index in range(4):
            print(f"\n--- Word {word_index}, Byte {byte_index} ---")
            for order in range(1, 5):
                d = higher_order_derivative_byte(state, word_index, byte_index, order, rounds=4)
                print(f"{order}-order derivative: 0x{d:02X}")

if __name__ == "__main__":
    test_all_bytes()

