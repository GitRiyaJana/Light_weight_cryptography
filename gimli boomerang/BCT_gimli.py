import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------
# Define nonlinear reversible 3-bit S-box
# -------------------------------------------------
sbox = [7,4,6,1,0,5,2,3]
n = len(sbox)

# Compute inverse S-box
sbox_inv = [0]*n
for i, v in enumerate(sbox):
    sbox_inv[v] = i

# -------------------------------------------------
# Compute Difference Distribution Table (DDT)
# -------------------------------------------------
def compute_ddt(sbox):
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
# Visualization helper
# -------------------------------------------------
def plot_table(table, title):
    plt.figure(figsize=(6, 5))
    plt.imshow(table, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Count')
    plt.title(title)
    plt.xlabel('Output Difference (b)')
    plt.ylabel('Input Difference (a)')
    for i in range(n):
        for j in range(n):
            plt.text(j, i, f"{table[i,j]}", ha='center', va='center', color='white', fontsize=10)
    plt.show()

# -------------------------------------------------
# Compute & plot both tables
# -------------------------------------------------
ddt = compute_ddt(sbox)
bct = compute_bct(sbox, sbox_inv)

print("S-box:", sbox)
print("Inverse:", sbox_inv)
print("\nDDT:\n", ddt)
print("\nBCT:\n", bct)

plot_table(ddt, "Difference Distribution Table (DDT)")
plot_table(bct, "Boomerang Connectivity Table (BCT)")

