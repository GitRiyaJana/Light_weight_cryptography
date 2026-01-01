# Toy Gimli Cipher Implementation

This repository contains a toy implementation of a Gimli-style permutation cipher in Python. It includes both encryption and decryption functions, along with a set of test vectors to verify its correctness.

## Files

- `Gimli_toy.py`: The main Python script containing the Gimli-style permutation implementation.
- `test_toy_gimli.py`: A Python script to run test vectors against the cipher implementation.
- `test_vectors.txt`: A collection of custom-generated test vectors.

## Prerequisites

To run this implementation, you only need:

- **Python 3**: The scripts are written in Python 3 and do not have any external library dependencies.

## How to Run

### Running the Toy Cipher

You can run the main `Gimli_toy.py` script to see an example of encryption and decryption with a predefined state.

```bash
python3 Gimli_toy.py
```

This will output the initial state, the state after each round of encryption, the final ciphertext, and then the decryption process to recover the original plaintext.

### Running the Tests

To verify the correctness of the encryption and decryption functions using the provided test vectors, run the `test_toy_gimli.py` script:

```bash
python3 test_toy_gimli.py
```

This script will encrypt and then decrypt each state defined in `test_vectors.txt`. It will report whether each test vector passed (i.e., the decrypted state matches the original state) and provide a summary at the end.

## Test Vectors

The `test_vectors.txt` file contains a series of custom-generated test vectors. Each test vector defines an initial state for the cipher, represented by three 4-byte arrays (x, y, z). The values are provided in hexadecimal format.

These test vectors are designed to cover various input scenarios and are used by `test_toy_gimli.py` to ensure the cipher's encryption and decryption processes are inverse operations and function as expected. They are not derived from any external standard or official Gimli test suite but are created specifically for this toy implementation.
