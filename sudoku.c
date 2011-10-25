/*
 * UNIVERSAL SUDOKU SOLVER
 * 7TH SEPTEMBER 2007
	* INPUT FILE EXAMPLE: 5 3 0 0 7 0 0 0 0
	*																				 6 0 0 1 9 5 0 0 0
	*																				 0 9 8 0 0 0 0 6 0
	*																				 8 0 0 0 6 0 0 0 3
	*																				 4 0 0 8 0 3 0 0 1
	*																				 7 0 0 0 2 0 0 0 6
	*																				 0 6 0 0 0 0 2 8 0
	*																				 0 0 0 4 1 9 0 0 5
	*																				 0 0 0 0 8 0 0 7 9
	*                    
*/


#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAX 9
#define TRUE 1
#define FALSE 0

//Prototypes
void copier(int from[MAX][MAX], int to[MAX][MAX]);
int checker(int dummy_grid[MAX][MAX], int x, int y, int num);
int uniq_updater(int orig_grid[MAX][MAX]);
int chance_updater(int dummy_grid[MAX][MAX], int x, int y, int chance_array[MAX]); 
int chance_solver(int dummy_grid[MAX][MAX], int x, int y, int chance_grid[MAX][MAX]);
void print(int grid[MAX][MAX]);
int is_complete(int grid[MAX][MAX]);

int solutions = 0;
void copier(int from[MAX][MAX], int to[MAX][MAX])
{
	int i, j;
	for(i = 0; i < MAX; ++i){
		for(j = 0; j < MAX; ++j){
			to[i][j] = from[i][j];
		}
	}
}

int checker(int dummy_grid[MAX][MAX], int x, int y, int num)
{
	int i, j, xfact, yfact, maxrt;
	for(i = 0; i < MAX; ++i){
		if((dummy_grid[x][i] == num && i != y) || (dummy_grid[i][y] == num && i != x))
			return FALSE;
	}
	maxrt = pow(MAX,0.5);
	xfact = (int) (x/maxrt);
	yfact = (int) (y/maxrt);
	for(i =  maxrt * xfact; i < maxrt * xfact + maxrt; i++)
		for(j = maxrt * yfact; j < maxrt * yfact + maxrt; j++)
			if(num == dummy_grid[i][j])
				return FALSE;
	return TRUE;
}

int uniq_updater(int orig_grid[MAX][MAX])
{
	int x, y , num, unique, chance_uniq, nsol, possible, complete;
	unique = TRUE;
	while(unique == TRUE){
		for(x = 0; x < MAX; ++x){
			for(y = 0; y < MAX; ++y){
				if(orig_grid[x][y] == 0){
					nsol = 0;
					for(num = 1; num <= MAX; ++num){
						possible = checker(orig_grid,x,y,num);
						if(possible){
							++nsol;
							chance_uniq = num;
						}
					}
					if(nsol == 1){
						orig_grid[x][y] = chance_uniq;
						unique = TRUE;
						complete = is_complete(orig_grid);
						if(complete)
							return TRUE;
					}
					else	//!
						unique = FALSE; //multiple sols.
				}
			}
		}
	}
	return unique;	//return to main and print final orig_grid
}

//For a particular sqaure checks all numbers possible 
int chance_updater(int dummy_grid[MAX][MAX],int x, int y, int chance_array[MAX])
{
	int k, impossible = TRUE;
		for(k = 0 ; k < MAX; ++k){
				if(checker(dummy_grid,x,y,k+1)){
					chance_array[k] = TRUE;
					impossible = FALSE;
				}
				else 
					chance_array[k] = FALSE;
		}
	return impossible;
}

//First call : chance_solver(dummy_grid,0,0,chance_grid); chance_grid=dummy_grid
//Recursive call : chance_solver(dummy_grid,x,y,new_chance_grid);
int chance_solver(int dummy_grid[MAX][MAX],int x, int y, int chance_grid[MAX][MAX])
{
	int i, contradiction;
       	int new_chance_grid[MAX][MAX], chance_array[MAX];
	if(dummy_grid[x][y] != 0){
		if(y == MAX - 1)
			chance_solver(dummy_grid,x+1,0,chance_grid);
	//	if(is_complete(chance_grid))
	//		print(chance_grid);
		else
			chance_solver(dummy_grid,x,y+1,chance_grid);
		return(0);
	}
	copier(chance_grid,new_chance_grid);
	contradiction = chance_updater(chance_grid,x,y,chance_array);
	if(contradiction)
		return FALSE;
	for(i = 0; i < MAX; ++i){
	       if(chance_array[i] == TRUE){
			new_chance_grid[x][y] = i + 1;
			if(is_complete(new_chance_grid))
				print(new_chance_grid);
	 		if(y == MAX - 1)
				chance_solver(dummy_grid,x+1,0,new_chance_grid);
			else
				chance_solver(dummy_grid,x,y+1,new_chance_grid);
	       }
	}
	return(0);
}

void print(int grid[MAX][MAX])
{
	
	int i,j,sroot;
	++solutions;		//global variable
	printf("Solution no. %d\n\n",solutions);
	sroot = pow(MAX,0.5);
	printf("\n");
	for(i = 0; i < MAX; i++){
		for(j = 0; j < MAX; j++){
			if(j == 0)
				printf(" ");
				printf(" %d ",grid[i][j]);
				if(j % sroot == sroot - 1)
				printf(" " );
		}
		printf("\n");
		if(i % sroot == sroot - 1)
			printf("\n");
	}
}

int is_complete(int grid[MAX][MAX])
{
	int i, j;
	for(i = 0; i < MAX; i++){
		for(j = 0; j < MAX; j++){
			if(grid[i][j] == 0)
				return FALSE;
		}
	}
	return TRUE;
}

int main(int argc, char** argv)
{
	int orig_grid[MAX][MAX], dummy_grid[MAX][MAX];
	int iret, solved, unique, i, j;
	FILE *fp;
        if(argc != 2){
		printf("Usage : %s <Sudoku Input File>\n",argv[0]);
		exit(1);
	}
	fp = fopen(argv[1],"r");
	for(i = 0; i < MAX; i++){
		for(j = 0; j < MAX; j++){
			fscanf(fp,"%d ",&orig_grid[i][j]);
		}
	}
	unique = uniq_updater(orig_grid);
	printf("\n\nUniversal Sudoku Solver by Sushant Bhadkamkar\n\n");
	if(unique){
		printf("Unique solution Sudoku\n\n");
		print(orig_grid);
		return(0);
	}
	printf("Multiple solution sudoku\n\n");
	copier(orig_grid,dummy_grid);
	solved = chance_solver(dummy_grid,0,0,dummy_grid);
	return(0);
}
