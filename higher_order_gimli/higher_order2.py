import itertools

# ---------------------------------------------------------
#  Your cipher here (replace with your own implementation)
# ---------------------------------------------------------
def gimli_encrypt(state, rounds=4):
    # state = (x[4], y[4], z[4])
    # Put your cipher here. This is a placeholder identity map.
    x, y, z = state
    return x[:], y[:], z[:]


# ---------------------------------------------------------
#  Generate bit-basis differences (correct!)
# ---------------------------------------------------------
def byte_basis_vectors():
    return [1 << i for i in range(8)]   # [1,2,4,8,16,32,64,128]


# ---------------------------------------------------------
#  Apply a difference to state
# ---------------------------------------------------------
def apply_diff(state, diffs):
    (x, y, z) = state
    x = x[:] ; y = y[:] ; z = z[:]
    for (layer, idx, val) in diffs:
        if layer == 'x': x[idx] ^= val
        if layer == 'y': y[idx] ^= val
        if layer == 'z': z[idx] ^= val
    return (x, y, z)


# ---------------------------------------------------------
#  Evaluate t‑th order derivative from basis vectors
# ---------------------------------------------------------
def higher_order_derivative(state, target, diffs, rounds=4):
    layer, pos = target
    xor_sum = 0

    # For all subsets of the difference vectors
    for r in range(len(diffs) + 1):
        for subset in itertools.combinations(diffs, r):
            st = apply_diff(state, subset)
            x, y, z = gimli_encrypt(st, rounds)

            # sign = parity of subset
            if (r % 2) == 1:
                sign = 1
            else:
                sign = 0

            val = {
                'x': x[pos],
                'y': y[pos],
                'z': z[pos],
            }[layer]

            if sign == 1:
                xor_sum ^= val

    return xor_sum


# ---------------------------------------------------------
#  Run 1st → 4th order derivatives
# ---------------------------------------------------------
def test_derivatives(rounds=4):
    # Initial state (all zero)
    state = ([0]*4, [0]*4, [0]*4)

    bytes_to_test = [('x',i) for i in range(4)] + \
                    [('y',i) for i in range(4)] + \
                    [('z',i) for i in range(4)]

    basis = byte_basis_vectors()

    print("\n=== Higher‑Order Derivatives (Correct Bit‑Basis Version) ===\n")

    for target in bytes_to_test:
        print(f"\n------ Target byte: {target[0]}[{target[1]}] ------")

        # 1st → 4th order
        for order in range(1, 5):
            diffs = []

            # Use first 'order' bit-difference vectors
            for b in basis[:order]:
                diffs.append((target[0], target[1], b))

            result = higher_order_derivative(state, target, diffs, rounds)
            print(f"{order}‑order derivative: {result:#04x}")


# ---------------------------------------------------------
if __name__ == "__main__":
    test_derivatives(rounds=4)

