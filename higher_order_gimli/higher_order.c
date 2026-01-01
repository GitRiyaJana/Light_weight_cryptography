#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define ROTL32(x,b) (((x)<<(b)) | ((x)>>(32-(b))))

void gimli_permutation(uint32_t state[12])
{
    uint32_t x, y, z;
    for(int round = 4; round>=1; round--) // reduced 4 rounds for demo
    {
        for(int col=0; col<4; col++)
        {
            x = ROTL32(state[col],24);
            y = ROTL32(state[col+4],9);
            z = state[col+8];

            state[col+8] = x^(z<<1)^((y&z)<<2);
            state[col+4] = y^x^((x|z)<<1);
            state[col] = z^y^((x&y)<<3);
        }

        if((round & 3)==0)
        {
            uint32_t t;
            t = state[0]; state[0]=state[1]; state[1]=t;
            t = state[2]; state[2]=state[3]; state[3]=t;
            state[0] ^= (0x9e377900 ^ round);
        }
        if((round & 3)==2)
        {
            uint32_t t;
            t = state[0]; state[0]=state[2]; state[2]=t;
            t = state[1]; state[1]=state[3]; state[3]=t;
        }
    }
}

void print_state_hex(uint32_t state[12])
{
    for(int i=0;i<12;i++)
    {
        printf("%08" PRIX32 " ", state[i]);
    }
    printf("\n");
}

// Generate bit-basis for 32-bit word
void generate_bit_basis(uint32_t basis[32])
{
    for(int i=0;i<32;i++)
        basis[i] = 1U << i;
}

// Apply subset of differences
void apply_diff(uint32_t base[12], uint32_t temp[12], int order, uint32_t basis[], uint32_t word_index, int subset)
{
    memcpy(temp, base, 12*sizeof(uint32_t));
    for(int i=0;i<order;i++)
    {
        if(subset & (1<<i))
            temp[word_index] ^= basis[i];
    }
}

// Compute t-th order derivative for one word
uint32_t compute_derivative(uint32_t base[12], uint32_t word_index, int order)
{
    uint32_t basis[32];
    generate_bit_basis(basis);

    uint32_t result = 0;
    uint32_t temp[12];

    for(int subset=0; subset < (1<<order); subset++)
    {
        apply_diff(base, temp, order, basis, word_index, subset);
        gimli_permutation(temp);
        result ^= temp[word_index];
    }
    return result;
}

int main()
{
    uint32_t state[12] = {1,0,0,0, 0,0,0,0, 0,0,0,0};
    printf("Initial state:\n"); print_state_hex(state);

    printf("\n=== Higher-Order Derivatives (1st to 4th order) ===\n");

    for(int w=0; w<12; w++)
    {
        printf("\n--- Word %d ---\n", w);
        for(int order=1; order<=4; order++)
        {
            uint32_t d = compute_derivative(state, w, order);
            printf("%d-order derivative: 0x%08X\n", order, d);
        }
    }
    return 0;
}

