"""
This script demonstrates a differential-linear distinguisher on a
two-round toy cipher where each round is just a 3-bit S-box.

The attack combines a differential characteristic over the first round (E0)
and a linear approximation over the second round (E1).
"""

import numpy as np
from LAT import compute_lat_bias

# -------------------------------------------------
# Define the 3-bit S-box from Gimli
# -------------------------------------------------
SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
N = len(SBOX)

# -------------------------------------------------
# Helper function to compute parity
# -------------------------------------------------
def parity(n):
    """Computes the parity of an integer (1 if odd number of set bits, 0 otherwise)."""
    return bin(n).count('1') % 2

# -------------------------------------------------
# Compute Difference Distribution Table (DDT)
# -------------------------------------------------
def compute_ddt(sbox):
    """Computes the DDT for a given S-box."""
    n = len(sbox)
    ddt = np.zeros((n, n), dtype=int)
    for alpha in range(n):
        for x in range(n):
            beta = sbox[x] ^ sbox[x ^ alpha]
            ddt[alpha][beta] += 1
    return ddt


# -------------------------------------------------
# Find the best differential-linear characteristic
# -------------------------------------------------
def find_best_characteristic(ddt, lat_bias):
    """
    Finds a list of the best characteristics (alpha, beta, delta) that 
    share the same maximum value of p * q^2.
    """
    max_correlation_sq = -1.0
    best_characteristics = []
    # Use a small tolerance for floating point comparisons
    tolerance = 1e-9

    # Iterate through all non-trivial input differences
    for alpha in range(1, N):
        # Iterate through all non-trivial intermediate differences/masks
        for beta in range(1, N):
            # Probability 'p' of the differential trail (alpha -> beta)
            p = ddt[alpha][beta] / N
            if p == 0:
                continue

            # Iterate through all non-trivial output masks
            for delta in range(1, N):
                # Correlation 'q' of the linear trail (beta -> delta)
                q = lat_bias[beta][delta] / (N / 2)
                
                # The effective squared correlation for the whole distinguisher
                p_q_sq = p * (q ** 2)

                if p_q_sq > max_correlation_sq + tolerance:
                    # Found a new maximum, clear the old list
                    max_correlation_sq = p_q_sq
                    best_characteristics = [(alpha, beta, delta, p, q, p_q_sq)]
                elif abs(p_q_sq - max_correlation_sq) < tolerance:
                    # Found another characteristic with the same max value
                    best_characteristics.append((alpha, beta, delta, p, q, p_q_sq))
    
    return best_characteristics

# -------------------------------------------------
# Main Differential-Linear Attack Demonstration
# -------------------------------------------------
def demonstrate_attack(num_pairs=200000):
    """
    Computes tables, finds the best characteristic(s), and runs the distinguisher for each.
    """
    print("--- Differential-Linear Attack Demonstration on 2-Round S-box Cipher ---")

    # 1. Compute tables
    ddt = compute_ddt(SBOX)
    lat_bias = compute_lat_bias(SBOX)
    print("\nComputed DDT:\n", ddt)
    print("\nComputed LAT Bias (LAT[u,v] - 4):\n", lat_bias)

    # 2. Find all optimal characteristics
    best_characteristics = find_best_characteristic(ddt, lat_bias)
    print(f"\n--- Step 1: Found {len(best_characteristics)} best characteristic(s) with p*q^2 ≈ {best_characteristics[0][5]:.6f} ---")
    
    for i, (alpha, beta, delta, p, q, p_q_sq) in enumerate(best_characteristics):
        print(f"\n--- Testing Trail {i+1}/{len(best_characteristics)}: α={alpha}, β={beta}, δ={delta} ---")
        
        # The sign of the correlation depends on the constant parity(gamma.beta). Here gamma=beta.
        correlation_sign = (-1)**parity(beta & beta)
        theoretical_correlation = correlation_sign * p * (q**2)

        # Define our simple 2-round cipher
        def e0(p_val):
            return SBOX[p_val]
        def e1(c_val):
            return SBOX[c_val]
        def cipher(p_val):
            return e1(e0(p_val))

        print(f"--- Running simulation for Trail {i+1} ---")

        # 3. Run the distinguisher in a single loop
        sum_of_terms = 0
        diff_hits_count = 0
        sum_dl_given_diff_hit = 0
        sum_dl_given_diff_miss = 0

        for _ in range(num_pairs):
            p_val = np.random.randint(0, N)
            p_prime_val = p_val ^ alpha

            y_val = e0(p_val)
            y_prime_val = e0(p_prime_val)

            c_val = e1(y_val)
            c_prime_val = e1(y_prime_val)

            linear_expr_val = parity(delta & c_val) ^ parity(delta & c_prime_val)
            current_term = (-1)**linear_expr_val
            sum_of_terms += current_term

            if (y_val ^ y_prime_val) == beta:
                diff_hits_count += 1
                sum_dl_given_diff_hit += current_term
            else:
                sum_dl_given_diff_miss += current_term

        # 4. Analyze results
        empirical_correlation = sum_of_terms / num_pairs
        stdev = np.sqrt(num_pairs)

        print(f"\n--- Analysis for Trail {i+1} ---")
        print(f"  Overall Empirical Correlation:   {empirical_correlation:.6f}")
        print(f"  Overall Theoretical Correlation: {theoretical_correlation:.6f}")

        print("\n  --- Intermediate Checks ---")
        empirical_diff_prob = diff_hits_count / num_pairs
        print(f"    Empirical Differential Probability (P -> Y): {empirical_diff_prob:.4f} (Expected: {p:.4f})")

        if diff_hits_count > 0:
            empirical_cond_corr_hit = sum_dl_given_diff_hit / diff_hits_count
            expected_cond_corr_hit = correlation_sign * (q**2)
            print(f"    Empirical Conditional Corr (L | diff holds): {empirical_cond_corr_hit:.6f} (Expected: {expected_cond_corr_hit:.6f})")
        
        diff_miss_count = num_pairs - diff_hits_count
        if diff_miss_count > 0:
            empirical_cond_corr_miss = sum_dl_given_diff_miss / diff_miss_count
            print(f"    Empirical Conditional Corr (L | diff misses): {empirical_cond_corr_miss:.6f} (Expected: ~0.000000)")

        if abs(sum_of_terms) > 3 * stdev:
            print(f"\n  SUCCESS: A significant correlation was detected ({abs(sum_of_terms)/stdev:.1f} std dev).")
        else:
            print(f"\n  FAILURE: Overall correlation not significant ({abs(sum_of_terms)/stdev:.1f} std dev).")


if __name__ == "__main__":
    demonstrate_attack(num_pairs=200000)
