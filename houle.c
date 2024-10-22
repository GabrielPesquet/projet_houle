#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "data-import.h"

#define XMAXS 200
#define XMAXR 200
#define YMAX 800
#define TMAX 120.0 // nombre de secondes de la simulation dans le monde réel
#define NTIMES 100.
#define MODEPROF 1 // 1 si basse profondeur, 0 si haute profondeur
#define NONDES 1
#define OUTPUT 0

double prof[XMAXR][YMAX];
double hauteur[XMAXR][YMAX];
const double dt = TMAX / NTIMES; // pas de temps arbitraire
const double dl = 1;			 // correspond à la distance entre deux cases
const double g = 9.81;
const double pi = 3.141592;

typedef struct Onde
{
	double lambda;
	double ***champ; // trois dimensions temps (3) x (XMAX) y (YMAX)
} onde;

onde ondes[NONDES];

onde new_onde(double longueur_onde)
{
	// fprintf(stderr, "✅ Here - new_onde");
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
{

	if (y == 0)
		return (champ[x + 1][y] + champ[x - 1][y] + champ[x][y + 1] + champ[x][YMAX - 1] - 4. * champ[x][y]) / (dl * dl);
	if (y == YMAX - 1)
		return (champ[x + 1][y] + champ[x - 1][y] + champ[x][0] + champ[x][y - 1] - 4. * champ[x][y]) / (dl * dl);

	return (champ[x + 1][y] + champ[x - 1][y] + champ[x][y + 1] + champ[x][y - 1] - 4. * champ[x][y]) / (dl * dl);
}

double calc_c(double lambda, int x, int y)
{
	// fprintf(stderr, "✅ Here - calc_c\n");
	// pour l'isntant seulement les deux modèles linéaires
	// ATTENTTION : lambda peut varier, c'est la pulsation qui bouge pas
	// fprintf(stderr, "x : %d, y : %d\n", x, y);
	return sqrt(g * prof[x][y]);
}

void init()
{
	/*for (int x = 0; x < XMAXR; x++){
		for (int y=0; y < YMAX; y++){
			hauteur[x][y] = 0;
			prof[x][y] = 10 + (1-0.5 * (double) x/XMAXR)*4 + sq((double) y/YMAX - 0.5)*6;
		}
	}*/
	// fprintf(stderr, "✅ Here - Init");
	float **elevations = get_elevations();
	for (int x = 0; x < XMAXR; x++)
	{
		// printf("%d\n", x);
		for (int y = 0; y < YMAX; y++)
		{
			if (x == 240)
			{
				// printf("%d\n", y);
			}
			hauteur[x][y] = 0;
			prof[x][y] = -(double)elevations[x][y];
		}
	}

	fprintf(stderr, "%f", elevations[0][0]);
	ondes[0] = new_onde(50.);
}

double coeffrot(int x)
{
	/*
	if (x < 3*XMAX/2){
		return 0.;
	}

	return exp(-1/sq(0.04*(2*XMAX-x)));
	*/

	return 0;
}

void futur_onde(onde w, int x, int y)
{
	// fprintf(stderr, "✅ Here - futur_onde");
	double c = calc_c(w.lambda, x, y);
	// fprintf(stderr, "✅ Here - futur_onde - 2");
	double lap = laplacien(w.champ[1], x, y);

	// fprintf(stderr, "✅ Here - futur_onde - 3");
	w.champ[2][x][y] = sq(dt * c) * lap + 2. * w.champ[1][x][y] - w.champ[0][x][y] - dt * dt * coeffrot(x) * sq(w.champ[1][x][y] - w.champ[0][x][y]);
	// fprintf(stderr, "✅ Here - futur_onde - 4\n");
}

void bords_onde(onde w, double t)
{
	// fprintf(stderr, "✅ Here - bords_onde");
	// doit être appelée après le calcul du futur du reste

	// bord haut pour l'instant un onde plane harmonique venant de x=0
	double c;
	for (int y = 0; y < YMAX; y++)
	{
		c = calc_c(w.lambda, 0, y);
		// w.champ[2][0][y] = exp(-sq(t/dt - 10));
		w.champ[2][0][y] = sin(2 * pi * t * c / w.lambda);
	}

	// fprintf(stderr, "✅ Here - bords_onde - 2");

	// bord bas
	double kappa; // juste pour les calculs
	for (int y = 0; y < YMAX; y++)
	{
		c = calc_c(w.lambda, 0, y);
		kappa = c * dt / dl;
		w.champ[2][XMAXR - 1][y] = w.champ[1][XMAXR - 2][y] + (w.champ[2][XMAXR - 2][y] - w.champ[1][XMAXR - 1][y]) * (kappa - 1) / (kappa + 1);
	}
	// fprintf(stderr, "✅ Here - bords_onde - 3");
}

void update_onde(onde w, double t)
{
	// fprintf(stderr, "✅ Here -uppdate_onde");
	// avancement futur -> présent -> passé par swap de pointeurs
	double **temp;
	temp = w.champ[0];
	w.champ[0] = w.champ[1];
	w.champ[1] = w.champ[2];
	w.champ[2] = temp;

	// calcul du nouveau futur
	for (int x = 1; x < XMAXR - 1; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			futur_onde(w, x, y);
		}
	}

	bords_onde(w, t);
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
		// fprintf(stderr, "🟧 Here - update_h");
		for (int x = 0; x < XMAXR; x++)
		{
			for (int y = 0; y < YMAX; y++)
			{
				// fprintf(stderr, "🟥 Here - update_h, (%d, %d)", x, y);
				hauteur[x][y] += ondes[i].champ[1][x][y];
			}
		}
	}

	// fprintf(stderr, "✅ End - update_h");
	// printf("%lf", hauteur[XMAX+10][YMAX/2]);
}

void savebin(FILE *fp)
{
	for (int x = 0; x < XMAXS; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			double a = hauteur[x][y];
			fwrite(&a, sizeof(double), 1, fp);
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
			if (hauteur[x][y] != hauteur[x][y])
			{
				printf("0. ");
			}
			else
			{
				printf("%.2lf ", hauteur[x][y]);
			}
		}
		printf("\n");
	}
}

int main()
{
	FILE *fp = fopen("data.bin", "wb");
	fprintf(stderr, "%d", three());
	double temps = 0;

	init();
	for (int i = 0; i < NTIMES; i++, temps += dt)
	{
		update_h(temps);
		// fprintf(stderr, "✅ Here - main");
		if (OUTPUT == 0)
			topython();
		fprintf(stderr, "✅ Here - to_python\n");
		if (OUTPUT == 1)
			savebin(fp);
		fprintf(stderr, "✅ Here - savebin\n");
	}
	fclose(fp);
}
