#!/usr/bin/env python3
# higher_order_diff.py
# Compute higher-order derivatives for the Gimli-style permutation
# (Uses the same permutation implementation as before)

ROUND_CONSTANT = 0x9e

# ---------- low-level helpers (rotations, sbox, swaps) ----------
def rotl8(x, n):
    return ((x << n) | (x >> (8 - n))) & 0xff

def rotr8(x, n):
    return ((x >> n) | (x << (8 - n))) & 0xff

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

def rotate_planes(x, y, z):
    return ([rotl8(w, 6) for w in x],
            [rotl8(w, 2) for w in y],
            z)

def small_swap(x, y, z):
    x = [x[1], x[0], x[3], x[2]]
    y = [y[1], y[0], y[3], y[2]]
    z = [z[1], z[0], z[3], z[2]]
    return x, y, z

def big_swap(x, y, z):
    x = [x[2], x[3], x[0], x[1]]
    y = [y[2], y[3], y[0], y[1]]
    z = [z[2], z[3], z[0], z[1]]
    return x, y, z

def add_round_constant(x, round_number):
    x = x[:]
    if round_number % 4 == 0:
        x[0] ^= (ROUND_CONSTANT ^ round_number)
    return x

# ---------- permutation (encryption) ----------
def gimli_encrypt(state, rounds=tuple(range(1, 13))):
    # rounds is an iterable of round numbers (example: range(1, N+1))
    x, y, z = state
    for r in rounds:
        x, y, z = rotate_planes(x, y, z)
        x, y, z = sbox_lanes(x, y, z)
        if r % 4 == 0:
            x, y, z = small_swap(x, y, z)
        elif r % 4 == 2:
            x, y, z = big_swap(x, y, z)
        x = add_round_constant(x, r)
    return x, y, z

# ---------- state helpers ----------
def zero_state():
    return ([0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0])

def xor_states(s1, s2):
    # XOR two states (tuple of three lists)
    return (
        [a ^ b for a, b in zip(s1[0], s2[0])],
        [a ^ b for a, b in zip(s1[1], s2[1])],
        [a ^ b for a, b in zip(s1[2], s2[2])],
    )

def make_single_byte_diff(plane, col, mask):
    """
    Build a state delta where `plane` in {'x','y','z'} and column col in 0..3
    is XORed with `mask` (0..255).
    """
    pidx = {'x': 0, 'y': 1, 'z': 2}[plane]
    s = ([0,0,0,0], [0,0,0,0], [0,0,0,0])
    s_list = list(s)
    s_list[pidx][col] = mask
    return tuple(s_list)

# ---------- higher-order derivative function ----------
def compute_higher_order_derivative(base_state, diffs, rounds_iterable, target_positions):
    """
    Compute t-th order derivative Δ_{d1,...,dt} f at base_state, where
    `diffs` is a list of t difference states (each a state tuple).
    `rounds_iterable` is passed to gimli_encrypt (e.g. range(1,5) for 4 rounds).
    `target_positions` is a list of tuples (plane, col) to inspect in output.
      plane in {'x','y','z'}, col in 0..3

    Returns a dict mapping (plane,col) -> XOR-value (0..255).
    This performs 2^t evaluations.
    """
    t = len(diffs)
    if t >= 25:
        # safety: 2^25 evaluations would be huge; adjust as needed
        raise ValueError("Too many diffs (2^t explodes). Keep t smaller.")

    accum = {(p, c): 0 for (p, c) in target_positions}

    # Iterate over all 2^t subsets
    for mask in range(1 << t):
        # build delta sum for this subset
        delta = zero_state()
        for i in range(t):
            if (mask >> i) & 1:
                delta = xor_states(delta, diffs[i])
        pt = xor_states(base_state, delta)
        ct = gimli_encrypt(pt, rounds=rounds_iterable)
        # collect target bytes
        for (p, c) in target_positions:
            pidx = {'x':0,'y':1,'z':2}[p]
            accum[(p, c)] ^= ct[pidx][c]
    return accum

# ---------- helpers to build basis diffs ----------
def full_byte_basis_for(plane, col):
    """Return list of 8 diffs, each flipping one bit inside the selected byte."""
    return [make_single_byte_diff(plane, col, 1 << b) for b in range(8)]

def combine_byte_bases(basis_list):
    """Concatenate multiple bases into one diffs list."""
    out = []
    for basis in basis_list:
        out.extend(basis)
    return out

# ---------- convenience experiment functions ----------
def test_full_byte_order(base_state=None, plane='x', col=0, rounds=4, targets=None):
    """
    Test the full 8-th order derivative on a single byte (i.e. basis of 8 single-bit diffs).
    If targets is None, test all output bytes.
    """
    if base_state is None:
        base_state = zero_state()
    diffs = full_byte_basis_for(plane, col)    # 8 diffs -> order 8
    if targets is None:
        targets = [(p, c) for p in ['x','y','z'] for c in range(4)]
    rounds_iter = range(1, rounds+1)
    result = compute_higher_order_derivative(base_state, diffs, rounds_iter, targets)
    return result

def test_two_full_bytes(base_state=None, a=('x',0), b=('x',1), rounds=4, targets=None):
    """
    Test combined 16-th order derivative by using the 8-bit basis on two bytes (order 16).
    WARNING: 2^16 = 65536 evaluations -> may be slow but still practical on modern machines.
    """
    if base_state is None:
        base_state = zero_state()
    basis_a = full_byte_basis_for(*a)
    basis_b = full_byte_basis_for(*b)
    diffs = combine_byte_bases([basis_a, basis_b])  # 16 diffs
    if targets is None:
        targets = [(p, c) for p in ['x','y','z'] for c in range(4)]
    rounds_iter = range(1, rounds+1)
    result = compute_higher_order_derivative(base_state, diffs, rounds_iter, targets)
    return result

# ---------- demo / CLI ----------
if __name__ == "__main__":
    print("Higher-order derivative experiments (this uses gimli_encrypt in this file).")

    # Example 1: full 8-th order derivative on x[0] after 4 rounds
    print("\nExample 1: Full 8th-order derivative on x[0], 4 rounds")
    res = test_full_byte_order(plane='x', col=0, rounds=4)
    for k, v in sorted(res.items()):
        print(f"target {k}: xor = {v:#04x}")
    # If all targets are 0 -> the 8th order derivative is zero everywhere (full-byte integral)

    # Example 2: check two bytes combined (order 16) on x[0] and x[1] after 4 rounds
    print("\nExample 2: Combined 16th-order derivative on x[0]+x[1], 4 rounds (2^16 evals)")
    res2 = test_two_full_bytes(a=('x',0), b=('x',1), rounds=4)
    zero_all = all(v == 0 for v in res2.values())
    print("All-zero?" , zero_all)
    # Print a few results
    cnt_nonzero = sum(1 for v in res2.values() if v != 0)
    print(f"Non-zero target bytes: {cnt_nonzero} (of {len(res2)})")

    # WARNING and advice
    print("\nNOTE: complexity grows as 2^t where t is number of difference vectors.")
    print(" - Single-byte full order is t=8 -> 256 encryptions.")
    print(" - Two bytes -> t=16 -> 65,536 encryptions.")
    print(" - Three bytes -> t=24 -> 16,777,216 encryptions (expensive).")
    print("Use derived-difference approach (basis vectors) rather than naive looping over full 256^k plaintexts.")


