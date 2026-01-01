
"""
This script provides an advanced demonstration of the boomerang attack
on a 3-bit S-box by first computing the DDT and BCT to find optimal trails,
and then constructing a valid boomerang quartet.
"""

import numpy as np

# -------------------------------------------------
# Define nonlinear reversible 3-bit S-box and its inverse
# -------------------------------------------------
SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
SBOX_INV = [SBOX.index(i) for i in range(len(SBOX))]
N = len(SBOX)

# -------------------------------------------------
# Compute Difference Distribution Table (DDT)
# -------------------------------------------------
def compute_ddt(sbox):
    """Computes the DDT for a given S-box."""
    n = len(sbox)
    ddt = np.zeros((n, n), dtype=int)
    for a in range(n):
        for x in range(n):
            dy = sbox[x] ^ sbox[x ^ a]
            ddt[a][dy] += 1
    return ddt

# -------------------------------------------------
# Compute Boomerang Connectivity Table (BCT)
# -------------------------------------------------
def compute_bct(sbox, sbox_inv):
    """Computes the BCT for a given S-box and its inverse."""
    n = len(sbox)
    bct = np.zeros((n, n), dtype=int)
    for a in range(n):
        for b in range(n):
            for x in range(n):
                lhs = sbox_inv[sbox[x] ^ b]
                rhs = sbox_inv[sbox[x ^ a] ^ b]
                if (lhs ^ rhs) == a:
                    bct[a][b] += 1
    return bct

# -------------------------------------------------
# Find optimal trails from DDT and BCT
# -------------------------------------------------
def find_optimal_trails(ddt, bct):
    """
    Finds a high-probability trail (alpha -> beta) from the DDT and a
    compatible high-probability intermediate difference (gamma) from the BCT.
    """
    # Find the best (alpha, beta) trail from DDT (highest probability, non-trivial)
    best_p = 0
    alpha, beta = 0, 0
    # Start from 1 to ignore the trivial alpha=0 case
    for a in range(1, N):
        for b_ in range(N):
            # Probability is count / N
            if ddt[a][b_] > best_p:
                best_p = ddt[a][b_]
                alpha, beta = a, b_

    # Find the best gamma for the chosen alpha from BCT
    best_q = 0
    gamma = 0
    # Start from 1 to ignore the trivial gamma=0 case
    for g in range(1, N):
        if bct[alpha][g] > best_q:
            best_q = bct[alpha][g]
            gamma = g
            
    p = best_p / N
    q = best_q / N

    return alpha, beta, p, gamma, q

# -------------------------------------------------
# Find a working plaintext for a given trail
# -------------------------------------------------
def find_plaintext_for_trail(alpha, beta):
    """Finds a plaintext P that satisfies SBOX(P) ^ SBOX(P^alpha) = beta."""
    for p_candidate in range(N):
        if (SBOX[p_candidate] ^ SBOX[p_candidate ^ alpha]) == beta:
            return p_candidate
    return None # Should not happen if the trail exists in DDT

# -------------------------------------------------
# Main boomerang demonstration
# -------------------------------------------------
def demonstrate_boomerang():
    """
    Computes tables, finds trails, and demonstrates the boomerang attack.
    """
    print("--- Boomerang Attack Demonstration on S-box ---")
    
    # 1. Compute tables
    ddt = compute_ddt(SBOX)
    bct = compute_bct(SBOX, SBOX_INV)
    print("\nComputed DDT:\n", ddt)
    print("\nComputed BCT:\n", bct)

    # 2. Find optimal trails automatically
    alpha, beta, p, gamma, q = find_optimal_trails(ddt, bct)
    print("\n--- Step 1: Automatically find high-probability trails ---")
    print(f"Found E0 trail (p={p:.2f}) from DDT: α={alpha} -> β={beta} (DDT[{alpha},{beta}]={ddt[alpha,beta]})")
    print(f"Found best intermediate diff for α={alpha} from BCT: γ={gamma} (BCT[{alpha},{gamma}]={bct[alpha,gamma]}, boomerang prob q={q:.2f})")

    # 3. Find a plaintext P that satisfies the E0 trail.
    P = find_plaintext_for_trail(alpha, beta)
    if P is None:
        print("Could not find a suitable plaintext. Exiting.")
        return
        
    P_prime = P ^ alpha
    print("\n--- Step 2: Find a plaintext pair (P, P') that follows the E0 trail ---")
    print(f"  Found P = {P} which satisfies SBOX({P}) ^ SBOX({P}^α) = β")
    print(f"  P       = {P}  (binary {P:03b})")
    print(f"  α       = {alpha}  (binary {alpha:03b})")
    print(f"  P'      = P ^ α = {P_prime}  (binary {P_prime:03b})")

    # 4. "Encrypt" through E0 (the forward S-box)
    C = SBOX[P]
    C_prime = SBOX[P_prime]
    print("\n--- Step 3: Encrypt through E0 (SBOX) ---")
    print(f"  C       = SBOX(P) = {C}")
    print(f"  C'      = SBOX(P') = {C_prime}")

    # 5. Verify that the intermediate difference is β
    intermediate_diff = C ^ C_prime
    print(f"\n>>> Verifying intermediate difference:")
    print(f"  C ^ C' = {C} ^ {C_prime} = {intermediate_diff}")
    if intermediate_diff == beta:
        print(f"  This matches our expected intermediate difference β = {beta}. The first trail holds true.")
    else:
        print(f"  This DOES NOT match β = {beta}. The demonstration has failed unexpectedly.")
        return

    # 6. Create a second pair (D, D') with difference γ
    D = C ^ gamma
    D_prime = C_prime ^ gamma
    print(f"\n--- Step 4: Create a new pair (D, D') with difference γ ---")
    print(f"  D       = C ^ γ = {C} ^ {gamma} = {D}")
    print(f"  D'      = C' ^ γ = {C_prime} ^ {gamma} = {D_prime}")

    # 7. "Decrypt" this pair through E1_inv (the inverse S-box)
    X = SBOX_INV[D]
    X_prime = SBOX_INV[D_prime]
    print(f"\n--- Step 5: Decrypt (D, D') through E1_inv (SBOX_INV) ---")
    print(f"  X       = SBOX_INV(D) = {X}")
    print(f"  X'      = SBOX_INV(D') = {X_prime}")

    # 8. Verify that the original difference α has returned
    final_diff = X ^ X_prime
    print(f"\n>>> Step 6: Verifying the final boomerang property <<<")
    print(f"  The final difference is X ^ X' = {X} ^ {X_prime} = {final_diff}")
    if final_diff == alpha:
        print(f"  SUCCESS! The final difference matches the original difference α = {alpha}.")
        print("  The boomerang has returned, forming the quartet (P, P', X, X').")
    else:
        print(f"  FAILURE! The boomerang failed. The final difference does not match α.")
        print("  This can happen even with good trails, as they are probabilistic.")

if __name__ == "__main__":
    demonstrate_boomerang()
