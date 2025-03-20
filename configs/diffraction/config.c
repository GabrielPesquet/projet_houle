#include "config.h" 

/* le but de ce set est purement d'étudier des interférences
 * ondulatoires, sans jouer sur la profondeur */

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


void init()
{
	init_cste(4.); // Partout hors du plan
}


void limites(double t){
	for (int i = 0 ; i < NONDES ; i++){
		bords(ondes[i]);
		limites_onde_point(ondes[i], t);	
		limites_mur_rect(ondes[i], 0,  YMAXS/2 - 2, XMAXS/2 - 15, YMAXS/2 + 2);		
		limites_mur_rect(ondes[i], XMAXS/2 + 15, YMAXS/2 - 2, XMAX-1, YMAXS/2 + 2);		
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

void limites_onde_point(onde w, double t)
	/* comme une goutte qui tombe */
{
	double c;
	//fprintf(stderr, "Au bord : %lf, ", gaussian(YMAX/6, mu, sigma));
	//fprintf(stderr, "au centre : %lf\n", gaussian(YMAX/2, mu, sigma));
	int xc = XMAXS/2 ; int yc = YMAXS/6 ; 
	c = calc_c(w.lambda, xc, yc);
	w.champ[2][xc][yc] = 5 *sin(2 * pi * t * c / w.lambda);

}

void limites_mur_rect(onde w, int x1, int y1, int x2, int y2){
	for (int x = x1 ; x <= x2 ; x ++ ){
		for (int y = y1 ; y <= y2 ; y++){
			w.champ[2][x][y] = 0 ; 
		}
	}
}
