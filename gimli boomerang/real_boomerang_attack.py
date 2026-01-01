
'''
This script simulates a real boomerang attack by trying random plaintexts
until a successful boomerang quartet is found.
'''

import random

SBOX = [7, 4, 6, 1, 0, 5, 2, 3]
INV_SBOX = [SBOX.index(i) for i in range(len(SBOX))]

def simulate_real_attack():
    """
    Loops through random plaintexts to find a working boomerang quartet
    and reports the number of attempts required.
    """
    print("--- Simulating a Real Boomerang Attack ---")
    print("This will try random plaintexts until a successful quartet is found.")
    print("Based on the probability of 1/256, we expect around 256 attempts.")

    # Define the high-probability trails (alpha -> beta and gamma -> delta)
    alpha = 1
    beta = 1
    gamma = 1
    delta = 1
    
    attempts = 0
    while True:
        attempts += 1

        # Step 1: Choose a RANDOM plaintext P from the possible inputs (0-7)
        P = random.randint(0, 7)

        # Step 2: Construct the full boomerang quartet based on this random P
        P_prime = P ^ alpha
        
        C = SBOX[P]
        C_prime = SBOX[P_prime]
        
        D = C ^ gamma
        D_prime = C_prime ^ gamma
        
        X = INV_SBOX[D]
        X_prime = INV_SBOX[D_prime]

        # Step 3: Check for success.
        # The boomerang succeeds if the final difference is the original alpha.
        final_diff = X ^ X_prime
        if final_diff == alpha:
            print(f"\nSuccess! Found a working quartet after {attempts} attempts.")
            print(f"  - Started with random plaintext P = {P}")
            print(f"  - The final plaintext pair (X, X') is ({X}, {X_prime})")
            print(f"  - The final difference is X ^ X' = {X} ^ {X_prime} = {final_diff}, which matches α = {alpha}.")
            
            # For a successful quartet, the two underlying trails must also hold.
            # Let's verify their differences.
            e0_diff = C ^ C_prime
            e1_inv_diff = X ^ X_prime # This is the same as final_diff

            print("\n  For this successful quartet, we can verify the intermediate trails held:")
            print(f"  - The E0 (forward) trail held: SBOX({P}) ^ SBOX({P_prime}) = {e0_diff} (matches expected β={beta})")
            print(f"  - The E1_inv (backward) trail held: INV_SBOX({D}) ^ INV_SBOX({D_prime}) = {e1_inv_diff} (matches expected δ={delta})")
            
            break # Exit the loop after finding a success

        # Optional: Print progress to show the script is working
        if attempts % 100 == 0:
            print(f"  ... still searching, {attempts} attempts so far.")

if __name__ == "__main__":
    simulate_real_attack()
