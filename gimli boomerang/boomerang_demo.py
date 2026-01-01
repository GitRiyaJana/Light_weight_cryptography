
'''
This script provides a concrete demonstration of the boomerang attack
properties on the 3-bit S-box used in the toy Gimli cipher.
'''

SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
INV_SBOX = [SBOX.index(i) for i in range(len(SBOX))]

def demonstrate_boomerang():
    """
    Constructs a boomerang quartet step-by-step to demonstrate
    how the attack works on the S-box.
    """
    print("--- Boomerang Attack Demonstration on S-box ---")

    # Step 1: Define the high-probability trails found in analyzer.py
    # Trail for E0 (forward S-box): α -> β
    alpha = 2
    beta = 1
    p = 0.25
    print(f"\nChosen E0 trail (p={p}): α={alpha} -> β={beta}")

    # Trail for E1_inv (inverse S-box): γ -> δ
    gamma = 2
    delta = 3
    q = 0.25
    print(f"Chosen E1_inv trail (q={q}): γ={gamma} -> δ={delta}")

    # Step 2: Find and select a plaintext P that satisfies the E0 trail.
    # We need P such that SBOX(P) ^ SBOX(P ^ α) = β.
    # From our DDT analysis, we know P=6 works for α=1, β=1 because:
    # SBOX(6) ^ SBOX(7) = 2 ^ 3 = 1.
    P = 6
    P_prime = P ^ alpha
    print(f"\nStarting with a plaintext pair (P, P') that follows the E0 trail:")
    print(f"  P       = {P}  (binary {P:03b})")
    print(f"  α       = {alpha}  (binary {alpha:03b})")
    print(f"  P'      = P ^ α = {P_prime}  (binary {P_prime:03b})")

    # Step 3: "Encrypt" through E0 (the forward S-box)
    C = SBOX[P]
    C_prime = SBOX[P_prime]
    print(f"\nEncrypting through E0 (SBOX):")
    print(f"  C       = SBOX(P) = {C}")
    print(f"  C'      = SBOX(P') = {C_prime}")

    # Step 4: Verify that the intermediate difference is β
    intermediate_diff = C ^ C_prime
    print(f"\n>>> Verifying intermediate difference:")
    print(f"  C ^ C' = {C} ^ {C_prime} = {intermediate_diff}")
    if intermediate_diff == beta:
        print(f"  This matches our expected intermediate difference β = {beta}. The first trail holds true.")
    else:
        print(f"  This DOES NOT match β = {beta}. The demonstration cannot continue.")
        return

    # Step 5: Create a second pair (D, D') with difference γ in the intermediate state
    D = C ^ gamma
    D_prime = C_prime ^ gamma
    print(f"\nCreating a new pair (D, D') in the intermediate state with difference γ:")
    print(f"  D       = C ^ γ = {C} ^ {gamma} = {D}")
    print(f"  D'      = C' ^ γ = {C_prime} ^ {gamma} = {D_prime}")

    # Step 6: "Decrypt" this pair through E1_inv (the inverse S-box)
    X = INV_SBOX[D]
    X_prime = INV_SBOX[D_prime]
    print(f"\nDecrypting (D, D') through E1_inv (INV_SBOX):")
    print(f"  X       = INV_SBOX(D) = {X}")
    print(f"  X'      = INV_SBOX(D') = {X_prime}")

    # Step 7: Verify that the original difference α has returned
    final_diff = X ^ X_prime
    print(f"\n>>> Verifying the final boomerang property:")
    print(f"  The final difference between the resulting plaintexts is X ^ X' = {final_diff}")
    if final_diff == alpha:
        print(f"  This matches the original difference α = {alpha}!")
        print("  The boomerang has returned successfully, forming the quartet (P, P', X, X').")
    else:
        print(f"  The boomerang failed. The final difference does not match α.")


if __name__ == "__main__":
    demonstrate_boomerang()
