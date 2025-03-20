#include "config.h" 

double max(double a, double b){
	return a < b ? b : a ; 
}
void init_cste(double cste)
{
	for (int x = 0; x < XMAX; x++)
	{
		for (int y = 0; y < YMAX; y++)
		{
			hauteur[x][y] = 0;
			prof[x][y] = cste; // ! A 4 ca dvg, pas à 3.........
							   // prof[x][y] = 10 + (1-0.5 * (double) x/XMAX)*4 + sq((double) y/YMAX - 0.5)*6;
		}
	}

	ondes[0] = new_onde(50.);
}


void init_gauss_ile(){
	double prof_min = -2. ; 
	double prof_max = 4. ;
	int rad = XMAX/ 2; 
	double sigma = (double) rad/3;
	int xc = XMAX/2 ; int yc = YMAX/2 ; 
	
	for (int x = xc - rad ; x < xc + rad ; x++){
		for (int y = yc - rad ; y < yc + rad ; y++){
			prof[x][y] = max(0, prof_max - (prof_max - prof_min)*gaussian(sqrt(sq(x-xc) + sq(y-yc)), 0, sigma));
		}
	}
	
	
}

void init()
{
	init_cste(4.); // Partout hors du plan
	init_gauss_ile() ;
}


void limites(double t){
	for (int i = 0 ; i < NONDES ; i++){
		bords(ondes[i]);
		limites_onde_gauss(ondes[i], t); 
	}
}

void bords(onde w){
	if (MODECIRC / 2 == 0){
		for (int x = 0 ; x < XMAX ; x++){
			w.champ[2][x][0] = 0.  ; w.champ[2][x][YMAX - 1] = 0. ;
		}
	}
	if (MODECIRC % 2 == 0) { //bords durs verticaux
		for (int y = 0 ; y < YMAX ; y++){
			w.champ[2][0][y] = 0. ; w.champ[2][XMAX - 1][y] = 0. ; 
		}
	}
}

void limites_onde_gauss(onde w, double t)
{
	double mu = (double) YMAX / 2;
	double sigma = YMAX * 0.04; // Pourquoi pas. Re : Pourquoi pas en effet 
	double c;
	int x_gen = XMAXR / 6;
	//fprintf(stderr, "Au bord : %lf, ", gaussian(YMAX/6, mu, sigma));
	//fprintf(stderr, "au centre : %lf\n", gaussian(YMAX/2, mu, sigma));
	for (int y = YMAX / 6; y < 5 * YMAX / 6; y++)
	{
		c = calc_c(w.lambda, x_gen, y);
		double g_factor = gaussian(y, mu, sigma);
		// g_factor = 1;
		// w.champ[2][0][y] = exp(-sq(t/dt - 10));
		if (t < 120) {
		w.champ[2][x_gen][y] = g_factor * sin(2 * pi * t * c / w.lambda);
		}

	}

}

double gaussian(double x, double mu, double sigma)
{
	// return 1 / (sigma * sqrt(2 * pi)) * exp(-0.5 * sq((x - mu) / sigma));
	return exp(-0.5 * sq((x - mu) / sigma));
}

