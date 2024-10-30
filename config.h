#ifndef CONFIG_H
#define CONFIG_H
#include "houle.h" 

#define XMAXS 500 // S pour shown
#define XMAXR 505 // R pour réel
#define YMAX 500
#define TMAX 120.0 // nombre de secondes de la simulation dans le monde réel
#define NTIMES 2000
#define MODEPROF 1 // 1 si basse profondeur, 0 si haute profondeur
#define MODECIRC 0
	// circmod : 0 pas de bord cylindrique 
	// circmod = 1 bords cylindriques X = 0 = XMAXR  
	// circmod = 2 bords cylindriques Y = 0 = YMAXR 
	// circmod = 3 bords X et Y
#define NONDES 1

extern double prof[XMAXR][YMAX];
extern double hauteur[XMAXR][YMAX];
extern const double dt; 
extern const double dl;

extern onde ondes[NONDES];

void init_plan_incline();
void init_cste(double cstei);
void bords(onde w);
void limites_onde_gauss(onde w, double t); 
double gaussian(double x, double mu, double sigma);

#endif
