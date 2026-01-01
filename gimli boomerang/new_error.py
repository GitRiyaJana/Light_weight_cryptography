"""
This script demonstrates the boomerang attack on a 3-bit S-box by first
computing the Boomerang Distribution Table (BDT) to find optimal (alpha, beta)
pairs, and then constructing a valid boomerang quartet.

BDT[α,β] = #{x : S(x) ⊕ S(x ⊕ α) = y, S⁻¹(y) ⊕ S⁻¹(y ⊕ β) = α}
"""

import numpy as np

# -------------------------------------------------
# Define S-box and its inverse
# -------------------------------------------------
SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
SBOX_INV = [SBOX.index(i) for i in range(len(SBOX))]
N = len(SBOX) # Size of the S-box (e.g., 2^3 = 8)

# -------------------------------------------------
# Compute Boomerang Distribution Table (BDT)
# -------------------------------------------------
def compute_bdt(sbox, sbox_inv):
    """
    Computes the Boomerang Distribution Table (BDT) for a given S-box.
    BDT[α,β] = #{x : S(x) ⊕ S(x ⊕ α) = y, S⁻¹(y) ⊕ S⁻¹(y ⊕ β) = α}
    """
    bdt = np.zeros((N, N), dtype=int)
    for alpha in range(N):
        for beta in range(N):
            for x in range(N):
                # Condition 1: S(x) ⊕ S(x ⊕ α) = y
                y = sbox[x] ^ sbox[x ^ alpha]
                
                # Condition 2: S⁻¹(y) ⊕ S⁻¹(y ⊕ β) = α
                # Need to handle cases where y or y^beta might be out of SBOX_INV domain
                # For a permutation S-box, SBOX_INV is defined for all values 0 to N-1
                # So y and y^beta will always be valid inputs to SBOX_INV
                if (sbox_inv[y] ^ sbox_inv[y ^ beta]) == alpha:
                    bdt[alpha][beta] += 1
    return bdt

# -------------------------------------------------
# Find the best (alpha, beta) pair from the BDT
# -------------------------------------------------
def find_best_bdt_pair(bdt):
    """
    Finds the (alpha, beta) pair with the highest count in the BDT,
    excluding trivial cases where alpha or beta is 0.
    """
    best_count = 0
    best_alpha, best_beta = 0, 0
    for alpha in range(1, N): # Exclude alpha=0
        for beta in range(1, N): # Exclude beta=0
            if bdt[alpha][beta] > best_count:
                best_count = bdt[alpha][beta]
                best_alpha, best_beta = alpha, beta
    return best_alpha, best_beta, best_count

# -------------------------------------------------
# Find a working plaintext for a given (alpha, beta) pair
# -------------------------------------------------
def find_plaintext_for_bdt_pair(sbox, sbox_inv, alpha, beta):
    """
    Finds a plaintext P that satisfies the BDT conditions for given alpha and beta.
    S(P) ⊕ S(P ⊕ α) = y
    S⁻¹(y) ⊕ S⁻¹(y ⊕ β) = α
    """
    for p_candidate in range(N):
        y = sbox[p_candidate] ^ sbox[p_candidate ^ alpha]
        if (sbox_inv[y] ^ sbox_inv[y ^ beta]) == alpha:
            return p_candidate
    return None # Should not happen if the BDT count is > 0

# -------------------------------------------------
# Main boomerang demonstration using BDT
# -------------------------------------------------
def demonstrate_boomerang_with_bdt():
    """
    Computes the BDT, finds optimal (alpha, beta) and demonstrates
    the boomerang attack.
    """
    print("--- Boomerang Attack Demonstration using Boomerang Distribution Table (BDT) ---")
    
    # 1. Compute the BDT
    bdt = compute_bdt(SBOX, SBOX_INV)
    print("\nComputed BDT:\n", bdt)

    # 2. Find the best (alpha, beta) pair from the BDT
    alpha, beta, count = find_best_bdt_pair(bdt)
    prob = count / N # Probability of the boomerang quartet
    print("\n--- Step 1: Find optimal (alpha, beta) from BDT ---")
    print("Found optimal (α=" + str(alpha) + ", β=" + str(beta) + ") from BDT with count=" + str(count) + " (probability=" + f"{prob:.2f}" + ")")

    # 3. Find a plaintext P that satisfies the BDT conditions for the chosen (alpha, beta).
    P = find_plaintext_for_bdt_pair(SBOX, SBOX_INV, alpha, beta)
    if P is None:
        print("Could not find a suitable plaintext for the chosen (alpha, beta) pair. Exiting.")
        return
        
    P_prime = P ^ alpha
    print("\n--- Step 2: Find a plaintext pair (P, P') that follows the initial difference α ---")
    print(f"  Found P = {P} which satisfies the BDT conditions for (α={alpha}, β={beta})")
    print("  P       = " + str(P) + "  (binary " + format(P, '03b') + ")")
    print("  α       = " + str(alpha) + "  (binary " + format(alpha, '03b') + ")")
    print("  P_prime = P ^ α = " + str(P_prime) + "  (binary " + format(P_prime, '03b') + ")")

    # 4. "Encrypt" through E0 (the forward S-box)
    C = SBOX[P]
    C_prime = SBOX[P_prime]
    print("\n--- Step 3: Encrypt through E0 (SBOX) ---")
    print("  C       = SBOX(P) = " + str(C))
    print("  C_prime = SBOX(P_prime) = " + str(C_prime))
    print("  Intermediate difference C ^ C_prime = " + str(C ^ C_prime))

    # 5. Create a second pair (D, D') by introducing difference β
    D = C ^ beta
    D_prime = C_prime ^ beta
    print(f"\n--- Step 4: Create a new pair (D, D') by introducing intermediate difference β ---")
    print("  β       = " + str(beta) + "  (binary " + format(beta, '03b') + ")")
    print("  D       = C ^ β = " + str(C) + " ^ " + str(beta) + " = " + str(D))
    print("  D_prime = C_prime ^ β = " + str(C_prime) + " ^ " + str(beta) + " = " + str(D_prime))

    # 6. "Decrypt" this pair through E1_inv (the inverse S-box)
    X = SBOX_INV[D]
    X_prime = SBOX_INV[D_prime]
    print(f"\n--- Step 5: Decrypt (D, D') through E1_inv (SBOX_INV) ---")
    print("  X       = SBOX_INV(D) = " + str(X))
    print("  X_prime = SBOX_INV(D_prime) = " + str(X_prime))

    # 7. Verify that the original difference α has returned
    final_diff = X ^ X_prime
    print(f"\n>>> Step 6: Verifying the final boomerang property <<<")
    print("  The final difference is X ^ X_prime = " + str(X) + " ^ " + str(X_prime) + " = " + str(final_diff))
    if final_diff == alpha:
        print("  SUCCESS! The final difference matches the original difference α = " + str(alpha) + ".")
        print("  The boomerang has returned, forming the quartet (P, P', X, X').")
    else:
        print("  FAILURE! The final difference does not match α.")
        print("  This can happen even with good (alpha, beta) pairs, as the BDT counts are probabilities.")

if __name__ == "__main__":
    demonstrate_boomerang_with_bdt()