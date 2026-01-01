#!/usr/bin/env python3
# gimli_reduced_integral.py
# Run reduced-round integral-style tests on Gimli (32-bit words).
from itertools import product
import time

def rol32(x, r):
    return ((x << r) & 0xFFFFFFFF) | ((x & 0xFFFFFFFF) >> (32 - r))

def gimli_perm32(state, rounds=24):
    st = state[:]
    for rnd in range(rounds, 0, -1):
        for col in range(4):
            x = rol32(st[col], 24)
            y = rol32(st[4+col], 9)
            z = st[8+col]
            st[8+col] = x ^ ((z << 1) & 0xFFFFFFFF) ^ ((y & z) << 2 & 0xFFFFFFFF)
            st[4+col] = y ^ x ^ (((x | z) << 1) & 0xFFFFFFFF)
            st[col]     = z ^ y ^ (((x & y) << 3) & 0xFFFFFFFF)
        if (rnd & 3) == 0:
            st[0], st[1] = st[1], st[0]
            st[2], st[3] = st[3], st[2]
        if (rnd & 3) == 2:
            st[0], st[2] = st[2], st[0]
            st[1], st[3] = st[3], st[1]
        if (rnd & 3) == 0:
            const = (rnd | 0x9e377900) & 0xFFFFFFFF
            st[0] ^= const
    return [x & 0xFFFFFFFF for x in st]

def test_lowbit_subspace(vary_indices, t_bits=8, fixed_values=None, rounds=6, show_progress=False):
    if fixed_values is None:
        fixed_values = {}
    base = [fixed_values.get(i, 0) & 0xFFFFFFFF for i in range(12)]
    k = len(vary_indices)
    xor_acc = [0]*12
    ranges = [range(1<<t_bits) for _ in range(k)]
    processed = 0
    start = time.time()
    for vals in product(*ranges):
        st = base[:]
        for idx, val in zip(vary_indices, vals):
            # set the low t_bits of word idx to val (keep high bits of base)
            st[idx] = (st[idx] & (~((1<<t_bits)-1))) | val
        out = gimli_perm32(st, rounds=rounds)
        for i in range(12):
            xor_acc[i] ^= out[i]
        processed += 1
        if show_progress and processed % 100000 == 0:
            print("Processed", processed)
    elapsed = time.time() - start
    zero = all(x == 0 for x in xor_acc)
    return zero, xor_acc, processed, elapsed

def run_suite():
    rounds_list = [6, 7, 8, 9, 10]   # reduced rounds to test
    tests = [
        ((0,), 8),
        ((0,), 12),
        ((0,), 16),
        ((0,1), 8),  # 2^16 combos
    ]
    for rnds in rounds_list:
        print("=== rounds =", rnds, "===")
        for idxs, t in tests:
            print("Test vary indices", idxs, "t_bits", t)
            zero, acc, cnt, elapsed = test_lowbit_subspace(idxs, t_bits=t, rounds=rnds)
            print(f"  count={cnt}, elapsed={elapsed:.2f}s, zero-sum={zero}")
            # optionally print xor accumulator (hex)
            print("  xor_acc (hex) =", [hex(x) for x in acc])
        print()

if __name__ == '__main__':
    run_suite()

