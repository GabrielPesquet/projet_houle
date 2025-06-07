#include <stdio.h>

#include "houle.h"
#include "config.h" 

#define OUTPUT 2 // bit 0 -> topython, bit 1 -> savebin
#define LAP    3 // 2 -> méthode naive d'o 2 
				 // 3 -> méthode d'o 2 lissé
				 // 4 -> méthode naive d'o 4

double prof[XMAX][YMAX];
double hauteur[XMAX][YMAX];
const double dt = TMAX / (double) NTIMES; // pas de temps de la simul  
const double dl = 1;					 // correspond à la distance entre deux cases
										 
onde ondes[NONDES]; // les ondes 

onde new_onde(double longueur_onde)
{
	double ***champ = malloc(3 * sizeof(double **));

	for (int i = 0; i < 3; i++)
	{
		champ[i] = malloc(XMAX * sizeof(double *));
		for (int x = 0; x < XMAX; x++)
		{
			champ[i][x] = malloc(YMAX * sizeof(double));
			for (int y = 0; y < YMAX; y++)
			{
				champ[i][x][y] = 0;
			}
		}
	}

	onde w = {longueur_onde, champ};
	return w;
}

double sq(double x)
{
	return x * x;
}

double laplacien(double **champ, int x, int y)
	// toujours calculé cylindrique suivant toutes les directions  
{
	if (LAP == 2){
	return (champ[(x + 1) % XMAX][y] + champ[(x + XMAX - 1) % XMAX][y] + champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX] 
			- 4. * champ[x][y]) / (dl * dl);
	}	

	if (LAP == 3){
	return (+0.10001*(champ[(x + 1) % XMAX][(y + YMAX - 1) % YMAX] + champ[(x + XMAX - 1) % XMAX][(y + 1) % YMAX] + champ[(x+1)%XMAX][(y + 1) % YMAX ] + champ[(x + XMAX -1)%XMAX][(y + YMAX - 1) % YMAX])
		   +0.9*(champ[(x + 1) % XMAX][y] + champ[(x + XMAX - 1) % XMAX][y] + champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX])
		   -4.*champ[x][y]) / (dl * dl);
	}

	if (LAP == 4){
	return (-0.0833*(champ[(x + 2) % XMAX][y] + champ[(x + XMAX - 2) % XMAX][y] + champ[x][(y + 2) % YMAX ] + champ[x][(y + YMAX - 2) % YMAX])
		   +1.3333*(champ[(x + 1) % XMAX][y] + champ[(x + XMAX - 1) % XMAX][y] + champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX])
		   -5.*champ[x][y]) / (dl * dl);
	}
}

//double laplacien_inc(double **champ, int x, int y)
//	// toujours calculé cylindrique suivant toutes les directions  
//	// ne comporte pas le terme forward
//{
//	if (LAP == 2){
//	return (champ[(x + 1) % XMAX][y] + champ[(x + XMAX - 1) % XMAX][y] + champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX])
//			-2. * champ[x][y] / (dl * dl);
//	}	
//
//	if (LAP == 3){
//	return (+0.5*(champ[(x + 1) % XMAX][(y + YMAX - 1) % YMAX] + champ[(x + XMAX - 1) % XMAX][(y + 1) % YMAX] + champ[(x+1)%XMAX][(y + 1) % YMAX ] + champ[(x + XMAX -1)%XMAX][(y + YMAX - 1) % YMAX])
//		   +0.5*(champ[(x + 1) % XMAX][y] + champ[(x + XMAX - 1) % XMAX][y] + champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX])
//		   ) / (dl * dl);
//	}
//
//	if (LAP == 4){
//	return (-0.0833*(champ[(x + 2) % XMAX][y] + champ[(x + XMAX - 2) % XMAX][y] + champ[x][(y + 2) % YMAX ] + champ[x][(y + YMAX - 2) % YMAX])
//		   +1.3333*(champ[(x + 1) % XMAX][y] + champ[(x + XMAX - 1) % XMAX][y] + champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX])
//		   ) / (dl * dl);
//	}
//}

double calc_c(double lambda, int x, int y)
{
	
	if (MODEPROF == 1) {
		//fprintf(stderr, "%lf \n", sqrt(g * prof[x][y])*dt/dl);
		return sqrt(g * prof[x][y]);
	}
	else return sqrt(g*lambda/(2*pi)) ; 
}

/*
double coeffrot(int x)
{
	if (x < 3*XMAX/2){
		return 0.;
	}

	return exp(-1/sq(0.04*(2*XMAX-x)));

	return 0;
}
*/

void futur_onde(onde w, int x, int y)
{
	double c = calc_c(w.lambda, x, y);
	double lap = laplacien(w.champ[1], x, y);
	w.champ[2][x][y] = (sq(dt * c) * lap + 2. * w.champ[1][x][y] - w.champ[0][x][y]) ; 
					  // - dt*dt*coeffrot(x)*sq(w.champ[1][x][y] - w.champ[0][x][y]);
}

void update_onde(onde w, double t)
{
	// avancement futur -> présent -> passé par swap de pointeurs

	double **temp;
	temp = w.champ[0];
	w.champ[0] = w.champ[1];
	w.champ[1] = w.champ[2];
	w.champ[2] = temp;

	// calcul du nouveau futur
	for (int x = 0; x < XMAX; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			futur_onde(w, x, y);
		}
	}
}

void update_h(double t)
{
	for (int x = 0; x < XMAX; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			hauteur[x][y] = 0;
		}
	}

	for (int i = 0; i < NONDES; i++)
	{
		update_onde(ondes[i], t);
		for (int x = 0; x < XMAX; x++)
		{
			for (int y = 0; y < YMAX; y++)
			{
				hauteur[x][y] += ondes[i].champ[1][x][y] ;
				//hauteur[x][y] = ondes[i].champ[1][x][y];
			}
		}
	}
	
	limites(t) ; 
	// printf("%lf", hauteur[XMAX+10][YMAX/2]);
}

void savebin(FILE *fp)
{
	for (int x = 0; x < XMAXS; x++)
	{
		for (int y = 0; y < YMAXS; y++)
		{
			fwrite(&hauteur[x][y], sizeof(double), 1, fp);
		}
	}
}

void topython()
{
	for (int x = 0; x < XMAXS; x++)
	{
		for (int y = 0; y < YMAXS; y++)
		{
			if (y)
			{
				printf(",");
			}
			printf("%.2lf ", hauteur[x][y]);
		}
		printf("\n");
	}
}

int main()
{
	FILE *fp = fopen("data.bin", "wb");
	double temps = 0;

	init();
	for (int i = 0; i < NTIMES; i++, temps += dt)
	{
		update_h(temps);
		if (OUTPUT % 2 == 1)
			if (i % 5 == 0) 
			topython();
		if (OUTPUT/2 == 1)
			savebin(fp);
	}
	fclose(fp);
}
