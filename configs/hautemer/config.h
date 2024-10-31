#ifndef CONFIG_H
#define CONFIG_H
#include "houle.h" 

#define XMAX 500 // réel 
#define XMAXS 500 // S pour shown
#define YMAX 500
#define YMAXS 500 
#define TMAX 100.0 // nombre de secondes de la simulation dans le monde réel
#define NTIMES 8000
#define MODEPROF 0 // 1 si basse profondeur, 0 si haute profondeur
#define MODECIRC 1
	// circmod : 0 pas de bord cylindrique 
	// circmod = 1 bords cylindriques X = 0 = XMAX  
	// circmod = 2 bords cylindriques Y = 0 = YMAXR 
	// circmod = 3 bords X et Y
#define NONDES 2

extern double prof[XMAX][YMAX];
extern double hauteur[XMAX][YMAX];
extern const double dt; 
extern const double dl;

extern onde ondes[NONDES];

void init_cste(double cste);
void bords(onde w);
void limites_onde_point(onde w, int xc, int yc, double t); 
void limites_mur_rect(onde w, int x1, int y1, int x2, int y2) ;
#endif
