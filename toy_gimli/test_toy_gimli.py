from Gimli_toy import gimli_encrypt, gimli_decrypt, print_state

def load_test_vectors_from_file(filepath):
    test_vectors = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Test Vector"):
                x_line = lines[i+1].strip()
                y_line = lines[i+2].strip()
                z_line = lines[i+3].strip()

                x = [int(byte, 16) for byte in x_line.split(': ')[1].split(' ')]
                y = [int(byte, 16) for byte in y_line.split(': ')[1].split(' ')]
                z = [int(byte, 16) for byte in z_line.split(': ')[1].split(' ')]
                test_vectors.append((x, y, z))
                i += 4 # Move past x, y, z lines and the empty line
            i += 1
    return test_vectors

def run_test_vectors():
    print("Running Gimli-style permutation test vectors...")
    TEST_VECTORS = load_test_vectors_from_file('test_vectors.txt')
    all_tests_passed = True
    for i, original_state in enumerate(TEST_VECTORS):
        # Encrypt
        encrypted_state = gimli_encrypt(original_state)

        # Decrypt
        decrypted_state = gimli_decrypt(encrypted_state)

        # Compare
        if original_state == decrypted_state:
            pass
        else:
            print(f"Test Vector {i+1}: FAILED")
            all_tests_passed = False
            print("Expected:")
            print_state(*original_state)
            print("Got:")
            print_state(*decrypted_state)
            
    if all_tests_passed:
        print("\nMy toy gimli is running correctly!")
    else:
        print("\nSome test vectors FAILED!")

if __name__ == "__main__":
    run_test_vectors()
