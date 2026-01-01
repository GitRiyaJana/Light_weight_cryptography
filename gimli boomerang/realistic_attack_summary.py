'''
This script performs a realistic boomerang attack simulation
and prints a concise summary of the probabilities.
'''

import random

SBOX = [7, 4, 6, 1, 0, 5, 2, 3]

def simulate_right_quartet_prob_summary():
    """
    Estimates the boomerang probability by randomly searching for right quartets
    and prints a concise summary.
    """
    # From analyzer.py, we know p=0.25 and q=0.25 for the best trails.
    # The theoretical probability of a right quartet is p² * q².
    p = 0.25
    q = 0.25
    theoretical_prob = (p**2) * (q**2)

    # We use the same high-probability differentials
    alpha = 1
    gamma = 1
    
    # We need a large number of trials for a good statistical estimate
    num_trials = 100000
    success_count = 0
    
    for i in range(num_trials):
        # In each trial, we pick two random plaintexts
        P = random.randint(0, 7)
        R = random.randint(0, 7)

        # Form the other two plaintexts in the potential quartet
        P_prime = P ^ alpha
        R_prime = R ^ alpha

        # Check if the two conditions for a 'right quartet' are met
        condition1 = (SBOX[P] ^ SBOX[R]) == gamma
        condition2 = (SBOX[P_prime] ^ SBOX[R_prime]) == gamma
        
        if condition1 and condition2:
            success_count += 1

    observed_prob = success_count / num_trials
    
    print(f"--- Realistic Boomerang Attack Summary ---")
    print(f"Theoretical Probability (p²*q²): {theoretical_prob:.6f} (1 in {1/theoretical_prob:.0f})")
    print(f"Observed Probability ({num_trials} trials): {observed_prob:.6f} (1 in {1/observed_prob:.2f})")

if __name__ == "__main__":
    simulate_right_quartet_prob_summary()
