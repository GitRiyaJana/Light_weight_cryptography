#!/usr/bin/env python3
# =============================================
# Impossible Differential Attack on 3-Round Toy-Gimli
# =============================================

import random
import toy_gimli
from toy_gimli import (
    inv_rotate_planes,
    inv_sbox_lanes,
    remove_round_constant,
    small_swap,
    big_swap,
    print_state,
    add_round_constant,
    sbox_lanes,
    rotate_planes
)

# ------------------------------------------- 
# 2-Round Impossible Differential
# ------------------------------------------- 
# We use a 2-round impossible differential of the form:
# Delta_in = ([d, 0, 0, 0], 0, 0) -> Delta_out = ([d', 0, 0, 0], 0, 0)
# where d and d' have a single bit set.
# This differential is impossible for rounds 24 and 23.

INPUT_DIFF = ([0x01, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0])
# We don't need to specify the output diff, just check if the planes other than x are zero.

# ------------------------------------------- 
# Key Recovery Attack
# ------------------------------------------- 

def recover_key(
    num_pairs=2 ** 10, rounds=(24, 23, 22), correct_key_r22=0x9E ^ 22
):
    """Recovers the last round subkey using an impossible differential.

    Args:
        num_pairs: The number of chosen-plaintext pairs to use.
        rounds: The rounds used for encryption.
        correct_key_r22: The correct subkey for the last round (for verification).
    """
    print("=== Impossible Differential Attack ===")
    print(f"Using {num_pairs} chosen-plaintext pairs.")

    # The round constant for the last round (r=22) is ROUND_CONSTANT ^ 22
    # We are attacking this subkey.
    possible_subkeys = list(range(256))

    for i in range(num_pairs):
        # 1. Generate a random plaintext P1
        p1 = (
            [random.randint(0, 255) for _ in range(4)],
            [random.randint(0, 255) for _ in range(4)],
            [random.randint(0, 255) for _ in range(4)],
        )

        # 2. Create P2 by XORing P1 with the input differential
        p2_x = [p1[0][j] ^ INPUT_DIFF[0][j] for j in range(4)]
        p2 = (p2_x, p1[1][:], p1[2][:])

        # 3. Encrypt both plaintexts to get C1 and C2
        # We don't need the full print output for the attack
        c1 = toy_gimli.gimli_encrypt_3rounds(p1, rounds, verbose=False)
        c2 = toy_gimli.gimli_encrypt_3rounds(p2, rounds, verbose=False)

        # 4. For each candidate subkey, check if it's impossible
        for subkey_guess in possible_subkeys[:]:
            # Partially decrypt C1 and C2 by one round
            c1_prime = partial_decrypt_one_round(c1, rounds[-1], subkey_guess)
            c2_prime = partial_decrypt_one_round(c2, rounds[-1], subkey_guess)

            # Calculate the difference after partial decryption
            diff_x = [c1_prime[0][j] ^ c2_prime[0][j] for j in range(4)]
            diff_y = [c1_prime[1][j] ^ c2_prime[1][j] for j in range(4)]
            diff_z = [c1_prime[2][j] ^ c2_prime[2][j] for j in range(4)]

            # Check for the impossible differential property
            # The difference should not be of the form ([d'], 0, 0)
            # This means diff_y and diff_z should not be all zero.
            if all(v == 0 for v in diff_y) and all(v == 0 for v in diff_z):
                # This subkey is impossible, so we remove it
                possible_subkeys.remove(subkey_guess)
                break  # Move to the next plaintext pair

    print("\n=== Attack Results ===")
    print(f"Correct subkey for round 22: {correct_key_r22}")
    print(f"Remaining possible subkeys: {possible_subkeys}")

    if correct_key_r22 in possible_subkeys:
        print("Attack successful! The correct subkey was not eliminated.")
    else:
        print("Attack failed! The correct subkey was eliminated.")


def partial_decrypt_one_round(state, r, subkey_guess):
    """Partially decrypts the state by one round with a guessed subkey."""
    x, y, z = state

    # Inverse of add_round_constant
    x = x[:]
    if r % 4 == 0:
        x[0] ^= subkey_guess

    # Inverse of swap
    combined = x + y + z
    if r % 4 == 0:
        combined = small_swap(combined)
    elif r % 4 == 2:
        combined = big_swap(combined)
    x, y, z = combined[0:4], combined[4:8], combined[8:12]

    # Inverse of S-box
    x, y, z = inv_sbox_lanes(x, y, z)

    # Inverse of rotation
    x, y, z = inv_rotate_planes(x, y, z)

    return x, y, z


# Monkey-patch the encryption function to accept a verbose flag
def gimli_encrypt_3rounds_silent(state, rounds, verbose=True):
    x, y, z = state
    if verbose: print_state(x, y, z, "Initial state")

    for r in rounds:
        if verbose: print(f"\n=== Round {r} (Encryption) ===")

        x, y, z = rotate_planes(x, y, z)
        if verbose: print_state(x, y, z, "After rotation")

        x, y, z = sbox_lanes(x, y, z)
        if verbose: print_state(x, y, z, "After S-box layer")

        combined = x + y + z
        if r % 4 == 0:
            combined = small_swap(combined)
            if verbose: print("Applied small swap")
        elif r % 4 == 2:
            combined = big_swap(combined)
            if verbose: print("Applied big swap")
        x, y, z = combined[0:4], combined[4:8], combined[8:12]
        if verbose: print_state(x, y, z, "After swap")

        x = add_round_constant(x, r)
        if verbose: print_state(x, y, z, "After round constant")

    if verbose: print("\n=== Final encrypted state ===")
    if verbose: print_state(x, y, z, "Ciphertext")
    return x, y, z

import toy_gimli
toy_gimli.gimli_encrypt_3rounds = gimli_encrypt_3rounds_silent


if __name__ == "__main__":
    # Run the attack
    recover_key()
