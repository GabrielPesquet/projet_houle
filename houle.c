#include <stdio.h>

#include "houle.h"
#include "config.h" 

#define OUTPUT 0 // 0 -> topython, 1 -> savebin

double prof[XMAXR][YMAX];
double hauteur[XMAXR][YMAX];
const double dt = TMAX / (double) NTIMES; // pas de temps de la simul  
const double dl = 1;					 // correspond à la distance entre deux cases
										 
onde ondes[NONDES]; // les ondes 

onde new_onde(double longueur_onde)
{
	double ***champ = malloc(3 * sizeof(double **));

	for (int i = 0; i < 3; i++)
	{
		champ[i] = malloc(XMAXR * sizeof(double *));
		for (int x = 0; x < XMAXR; x++)
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
	return (champ[(x + 1) % XMAXR][y] + champ[(x + XMAXR - 1) % XMAXR][y]
		   	+ champ[x][(y + 1) % YMAX ] + champ[x][(y + YMAX - 1) % YMAX] - 4. * champ[x][y]) / (dl * dl);
}

double calc_c(double lambda, int x, int y)
{
	// pour l'instant seulement modèle basse profondeur 
	// ATTENTTION : lambda peut varier, c'est la pulsation qui bouge pas
	// Re ATTENTTION : jsp si c'est moi qui aimis ça, il faudrait revoir toute la manière dont sont traitées les ondes...
	return sqrt(g * prof[x][y]);
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
	// erreur (homogénéité) dans l'Overleaf ? p.12
	// C'est quoi coeffrot ? 
	// Ah bah ça vaut 0...
	// Re : c'est un vestige ...
	w.champ[2][x][y] = sq(dt * c) * lap + 2. * w.champ[1][x][y] - w.champ[0][x][y]; // - dt*dt*coeffrot(x)*sq(w.champ[1][x][y] - w.champ[0][x][y]);
}


void bords_onde(onde w, double t)
{
	// doit être appelée après le calcul du futur du reste

	// bord haut pour l'instant un onde plane harmonique venant de x=0
	double c;
	int x_gen = XMAXS / 6;
	for (int y = YMAX / 3; y < 2 * YMAX / 3; y++)
	{
		c = calc_c(w.lambda, x_gen, y);
		// w.champ[2][0][y] = exp(-sq(t/dt - 10));
		w.champ[2][x_gen][y] = sin(2 * pi * t * c / w.lambda);
	}
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
	for (int x = 0; x < XMAXR; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			futur_onde(w, x, y);
		}
	}
	// bords_onde(w, t);
}

void update_h(double t)
{
	for (int x = 0; x < XMAXR; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			hauteur[x][y] = 0;
		}
	}

	for (int i = 0; i < NONDES; i++)
	{
		update_onde(ondes[i], t);
		for (int x = 0; x < XMAXR; x++)
		{
			for (int y = 0; y < YMAX; y++)
			{
				// hauteur[x][y] += ondes[i].champ[1][x][y] ;
				hauteur[x][y] = ondes[i].champ[1][x][y];
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
		for (int y = 0; y < YMAX; y++)
		{
			fwrite(&hauteur[x][y], sizeof(double), 1, fp);
		}
	}
}

void topython()
{
	for (int x = 0; x < XMAXS; x++)
	{
		for (int y = 0; y < YMAX; y++)
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
		if (OUTPUT == 0)
			if (i % 10 == 0) 
			topython();
		if (OUTPUT == 1)
			savebin(fp);
	}
	fclose(fp);
}
