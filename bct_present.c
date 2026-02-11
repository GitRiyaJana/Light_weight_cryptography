#include <stdio.h>
#include <stdint.h>

#define SBOX_SIZE 16

int SBOX[SBOX_SIZE] = {12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2};

int INV_SBOX[SBOX_SIZE] = {5, 14, 15, 8, 12, 1, 2, 13, 11, 4, 6, 3, 0, 7, 9, 10};

void compute_bct(int sbox[], int inv_sbox[], int bct[16][16]){
	for(int a=0;a<16;a++)
	{
		for(int b=0;b<16;b++)
		{
			int count=0;
			for(int x=0;x<16;x++)
			{
			int y1=inv_sbox[sbox[x]^b];
			int y2=inv_sbox[(sbox[x^a])^b];
			if((y1^y2)==a)
				count++;
			}
			bct[a][b]=count;
		}
		
	}
	
	printf("  ");
	for(int b=0;b<16;b++)
		printf("%2x ", b);
	printf("\n------------------------------------------------------------\n");
	
	for(int a=0;a<16;a++)
	{
		printf("%2x | ",a);
		
		for(int b=0;b<16;b++)
			printf("%2d ",bct[a][b]);
		printf("\n");
		
	}
}

int main()
{
	int bct[16][16];
	compute_bct(SBOX,INV_SBOX,bct);
	return 0;
}

