#include <stdio.h>
#include <stdint.h>

#define SBOX_SIZE 8

//  S-box
int SBOX[SBOX_SIZE]     = {7, 4, 6, 1, 0, 5, 2, 3};
// Inverse S-box
int INV_SBOX[SBOX_SIZE] = {4, 3, 6, 7, 1, 5, 2, 0};

// Compute Boomerang Connectivity Table (BCT)
void compute_bct(int sbox[], int inv_sbox[], int bct[8][8]) {
    for (int a = 0; a < 8; a++) {
        for (int b = 0; b < 8; b++) {
            int count = 0;
            for (int x = 0; x < 8; x++) {
                int y1 = inv_sbox[sbox[x] ^ b];
                int y2 = inv_sbox[sbox[x ^ a] ^ b];
                if ((y1 ^ y2) == a)
                    count++;
            }
            bct[a][b] = count;
        }
    }
}

// Compute Boomerang Difference Table (BDT)
void compute_bdt(int sbox[], int inv_sbox[], int bdt[8][8][8]) {
    for (int d0 = 0; d0 < 8; d0++) {
        for (int d1 = 0; d1 < 8; d1++) {
            for (int nabla0 = 0; nabla0 < 8; nabla0++) {
                int count = 0;
                for (int x = 0; x < 8; x++) {
                    int y1 = inv_sbox[sbox[x] ^ nabla0];
                    int y2 = inv_sbox[sbox[x ^ d0] ^ nabla0];
                    if ((y1 ^ y2) == d1)
                        count++;
                }
                bdt[d0][d1][nabla0] = count;
            }
        }
    }
}

// Print BCT
void print_bct(int bct[8][8]) {
    printf("\n==============================\n");
    printf("Boomerang Connectivity Table (BCT)\n");
    printf("==============================\n\n");

    printf("    ");
    for (int j = 0; j < 8; j++)
        printf("%2X ", j);
    printf("\n------------------------------------------------------\n");

    for (int i = 0; i < 8; i++) {
        printf("%2X | ", i);
        for (int j = 0; j < 8; j++)
            printf("%2d ", bct[i][j]);
        printf("\n");
    }
}

// Print BDT layer-by-layer
void print_bdt(int bdt[8][8][8]) {
    printf("\n==============================\n");
    printf("Boomerang Difference Table (BDT)\n");
    printf("==============================\n");

    for (int d0 = 0; d0 < 8; d0++) {
        printf("\n-- For Δ0 = %X --\n", d0);
        printf("    ");
        for (int nabla0 = 0; nabla0 < 8; nabla0++)
            printf("%2X ", nabla0);
        printf("\n------------------------------------------------------\n");

        for (int d1 = 0; d1 < 8; d1++) {
            printf("%2X | ", d1);
            for (int nabla0 = 0; nabla0 < 8; nabla0++)
                printf("%2d ", bdt[d0][d1][nabla0]);
            printf("\n");
        }
    }
}

int main() {
    int bct[8][8];
    int bdt[8][8][8];

    // Compute both tables
    compute_bct(SBOX, INV_SBOX, bct);
    compute_bdt(SBOX, INV_SBOX, bdt);

    // Print tables
    print_bct(bct);
    print_bdt(bdt);

    // Verify property
    printf("\n==============================\n");
    printf("Verification: BCT(Δ0,∇0) = ΣΔ1 BDT(Δ0,Δ1,∇0)\n");
    printf("==============================\n");

    int all_ok = 1;
    int valid_count = 0;

    for (int d0 = 0; d0 < 8; d0++) {
        for (int nabla0 = 0; nabla0 < 8; nabla0++) {
            int sum = 0;
            for (int d1 = 0; d1 < 8; d1++)
                sum += bdt[d0][d1][nabla0];

            if (sum == bct[d0][nabla0]) {
                printf("✔ Valid: Δ0=%X, ∇0=%X  (Sum=%d, BCT=%d)\n",
                       d0, nabla0, sum, bct[d0][nabla0]);
                valid_count++;
            } else {
                printf("✖ Mismatch: Δ0=%X, ∇0=%X  (Sum=%d, BCT=%d)\n",
                       d0, nabla0, sum, bct[d0][nabla0]);
                all_ok = 0;
            }
        }
    }

    printf("\nTotal valid entries: %d / 64\n", valid_count);
    if (all_ok)
        printf("\n All entries verified successfully!\n");
    else
        printf("\nMismatch found but\n%d valid Entries Found.\n",valid_count);

    return 0;
}

