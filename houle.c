#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#define XMAX 200 // 200 utilisés + 150 de sécurité + 50 d'amortissement pour être sûr et certain qu'il n'y a pas d'effets de bord 
#define YMAX 200 
#define TMAX 30.0 // nombre de secondes de la simulation dans le monde réel 
#define NTIMES 1000.
#define MODEPROF 1 // 1 si basse profondeur, 0 si haute profondeur 
#define NONDES 1

double prof[2*XMAX][YMAX] ;
double hauteur[2*XMAX][YMAX] ; 
const double dt = TMAX/NTIMES; //pas de temps arbitraire
const double dl = 1; //correspond à la distance entre deux cases
const double g = 9.81;
const double pi = 3.141592 ;

typedef struct Onde{
	double lambda; 
	double *** champ; //trois dimensions temps (3) x (XMAX) y (YMAX)
} onde ;

onde ondes[NONDES] ;

onde new_onde(double longueur_onde){
	double *** champ = malloc(3 * sizeof(double**) );
	
	for (int i = 0; i < 3; i++){	
		champ[i] = malloc(2*XMAX*sizeof(double*));
		for (int x = 0; x < 2*XMAX; x++){
			champ[i][x] = malloc(YMAX * sizeof(double));
			for (int y = 0; y < YMAX; y++){
				champ[i][x][y] = 0 ; 

			}
		}
	}	
	
	onde w = {longueur_onde, champ}; 	
	return w; 
}

double sq(double x) {
	return x*x; 
}

double laplacien(double ** champ, int x , int y) {
	if (y==0) return (champ[x+1][y] + champ[x-1][y] + champ[x][y+1] + champ[x][YMAX-1] - 4.*champ[x][y])/(dl*dl);
	if (y==YMAX-1) return (champ[x+1][y] + champ[x-1][y] + champ[x][0] + champ[x][y-1] - 4.*champ[x][y])/(dl*dl);
	return (champ[x+1][y] + champ[x-1][y] + champ[x][y+1] + champ[x][y-1] - 4.*champ[x][y])/(dl*dl);
}

double calc_c(double lambda, int x, int y){
	// pour l'isntant seulement les deux modèles linéaires 
	if (MODEPROF == 0) return  0.;
	if (MODEPROF == 1) return sqrt(g*prof[x][y]);
}

void init(){
	//sera remplacé par un fichier à part avec différents préset plus tard si j'ai la foi 
	for (int x = 0; x < 2*XMAX; x++){
		for (int y=0; y < YMAX; y++){
			hauteur[x][y] = 0;
			prof[x][y] = 10 + (1-0.5 * (double) x/XMAX)*4 + sq((double) y/YMAX - 0.5)*4; 
		}
	}	

	ondes[0] = new_onde(50.);
}

double coeffrot(int x){
	if (x < 2*XMAX - 50){
		return 0.; 
	}	
	
	//if (x <= 50) return 30*exp(-1/sq(dl*x));
	return 30*exp(-1/sq(dl*(2*XMAX-x)));
}

void futur_onde(onde w, int x, int y) {
	double c = calc_c(w.lambda, x, y);	
	double lap = laplacien(w.champ[1], x, y) ;
	
	w.champ[2][x][y] = sq(dt*c)*lap 
		             + 2.*w.champ[1][x][y]- w.champ[0][x][y] 
					 - dt*coeffrot(x)*(w.champ[1][x][y] - w.champ[0][x][y]) ; 
}

void bords_onde(onde w, double t){
	// pour l'instant un onde plane harmonique venant de x=0
	double c;
	for (int y = 0; y < YMAX; y++){
		c = calc_c(w.lambda, 0, y);
		//w.champ[2][0][y] = exp(-sq(t/dt - 10)); 
		w.champ[2][0][y] = sin(2*pi*t*c/w.lambda);  

	}
	
}

void update_onde(onde w, double t){
	//avancement futur -> présent -> passé par swap de pointeurs 
	double ** temp;
	temp = w.champ[0] ;
	w.champ[0] = w.champ[1] ;
	w.champ[1] = w.champ[2] ;
	w.champ[2] = temp ;

	//calcul du nouveau futur 
	for (int x = 1; x < 2*XMAX - 1 ; x++){
		for (int y = 0; y < YMAX; y++){
			futur_onde(w,x,y);
		}
	}

	bords_onde(w,t);
}

void update_h(double t){
	for (int x = 0; x < XMAX ; x++){
		for (int y = 0; y < YMAX ; y++){
			hauteur[x][y] = 0 ;
		}
	}

	for (int i = 0; i < NONDES ; i++){
		update_onde(ondes[i], t); 
		for (int x = 0; x < XMAX ; x++){
			for (int y = 0 ; y < YMAX ; y ++ ){
				hauteur[x][y] += ondes[i].champ[1][x][y] ;
			}
		}
	}
}

void savebin(FILE * fp){
	for (int x = 0; x < XMAX; x++){
		for (int y = 0 ; y < YMAX; y++){
			fwrite(&hauteur[x][y], sizeof(double), 1, fp);
		}
	}
}

int main(){
	FILE * fp = fopen("data.bin", "wb");
	double temps = 0; 

	init(); 
	for (int i = 0; i < NTIMES; i++, temps+= dt){
		update_h(temps);
		savebin(fp);
	}	
	fclose(fp);
}
