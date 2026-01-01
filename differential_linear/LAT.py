"""
This file contains the function to compute the Linear Approximation Table (LAT)
for a given S-box, which is a core component in linear cryptanalysis.
"""

import numpy as np

# -------------------------------------------------
# Helper function to compute parity
# -------------------------------------------------
def parity(n):
    """Computes the parity of an integer (1 if odd number of set bits, 0 otherwise)."""
    return bin(n).count('1') % 2

# -------------------------------------------------
# Compute Linear Approximation Table (LAT)
# -------------------------------------------------
def compute_lat_bias(sbox):
    """
    Computes the LAT bias table for a given S-box.
    The values are LAT[u,v] - N/2, where N is the size of the S-box.
    """
    n = len(sbox)
    lat_bias = np.zeros((n, n), dtype=int)
    for u in range(n):  # Input mask
        for v in range(n):  # Output mask
            count = 0
            for x in range(n):
                if parity(u & x) == parity(v & sbox[x]):
                    count += 1
            lat_bias[u][v] = count - n // 2
    return lat_bias
