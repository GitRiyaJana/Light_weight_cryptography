
import math

# The S-box from your enc_dec_gim.py file
SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
# The inverse S-box, required for the E1 part of the boomerang attack
INV_SBOX = [SBOX.index(i) for i in range(len(SBOX))]

def calculate_ddt(sbox):
    """Calculates the Differential Distribution Table (DDT) for a given S-box."""
    sbox_size = len(sbox)
    # Initialize an empty DDT table (e.g., 8x8 for a 3-bit S-box)
    ddt = [[0] * sbox_size for _ in range(sbox_size)]

    # Iterate over all possible input pairs to find differences
    for x1 in range(sbox_size):
        for x2 in range(sbox_size):
            input_diff = x1 ^ x2
            output_diff = sbox[x1] ^ sbox[x2]
            ddt[input_diff][output_diff] += 1
    return ddt

def print_ddt(ddt):
    """Prints the DDT in a readable format."""
    sbox_size = len(ddt)
    header = "      " + " ".join(f"{i:^3}" for i in range(sbox_size))
    print(header)
    print("    " + "-" * (len(header) - 4))
    for i, row in enumerate(ddt):
        row_str = f"  {i} | " + " ".join(f"{val:^3}" for val in row)
        print(row_str)

def find_best_trail(ddt):
    """Finds the most probable non-trivial differential trail from a DDT."""
    sbox_size = len(ddt)
    max_count = 0
    best_alpha = -1
    best_beta = -1
    # Start alpha from 1 to ignore the trivial (0 -> 0) differential
    for alpha in range(1, sbox_size):
        for beta in range(sbox_size):
            if ddt[alpha][beta] > max_count:
                max_count = ddt[alpha][beta]
                best_alpha = alpha
                best_beta = beta
    
    probability = max_count / sbox_size
    return best_alpha, best_beta, probability, max_count

def main():
    """
    Performs a boomerang attack analysis on the S-box alone.
    """
    print("--- Analyzing S-box for Boomerang Attack ---")

    # --- Part 1: Analyze the forward S-box to find a trail for E0 ---
    print("\n[E0 Analysis - Forward S-box]")
    ddt_forward = calculate_ddt(SBOX)
    print("DDT for forward S-BOX (α -> β):")
    print_ddt(ddt_forward)
    alpha, beta, p, p_count = find_best_trail(ddt_forward)
    print(f"\nFound best trail for E0 (α -> β): {alpha} -> {beta}")
    print(f"This trail holds for {p_count} out of {len(SBOX)} possible inputs.")
    print(f"Probability p = {p_count}/{len(SBOX)} = {p}")

    # --- Part 2: Analyze the inverse S-box to find a trail for E1 ---
    print("\n[E1 Analysis - Inverse S-box]")
    print(f"Inverse S-BOX: {INV_SBOX}")
    ddt_inverse = calculate_ddt(INV_SBOX)
    print("\nDDT for inverse S-BOX (γ -> δ):")
    print_ddt(ddt_inverse)
    gamma, delta, q, q_count = find_best_trail(ddt_inverse)
    print(f"\nFound best trail for E1_inv (γ -> δ): {gamma} -> {delta}")
    print(f"This trail holds for {q_count} out of {len(INV_SBOX)} possible inputs.")
    print(f"Probability q = {q_count}/{len(INV_SBOX)} = {q}")

    # --- Part 3: Calculate the final boomerang probability ---
    print("\n[Boomerang Attack Probability Calculation]")
    boomerang_prob = (p**2) * (q**2)
    print(f"The boomerang probability is given by p² * q²")
    print(f"p² = ({p})² = {p**2}")
    print(f"q² = ({q})² = {q**2}")
    print(f"Total Probability = {p**2} * {q**2} = {boomerang_prob}")
    if boomerang_prob > 0:
      print(f"This is approximately 1 in {1/boomerang_prob:.0f} chance.")

if __name__ == "__main__":
    main()
