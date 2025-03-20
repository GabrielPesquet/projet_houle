#ifndef CONFIG_H
#define CONFIG_H
#include "houle.h" 

#define XMAXS 500 // S pour shown
#define XMAX 1000 // réel 
#define YMAX 1000
#define YMAXS 500 
#define TMAX 240.0 // nombre de secondes de la simulation dans le monde réel
#define NTIMES 4000
#define MODEPROF 1 // 1 si basse profondeur, 0 si haute profondeur
#define MODECIRC 3
	// circmod : 0 pas de bord cylindrique 
	// circmod = 1 bords cylindriques X = 0 = XMAX  
	// circmod = 2 bords cylindriques Y = 0 = YMAXR 
	// circmod = 3 bords X et Y
#define NONDES 1

extern double prof[XMAX][YMAX];
extern double hauteur[XMAX][YMAX];
extern const double dt; 
extern const double dl;

extern onde ondes[NONDES];

void init_cste(double cste);
void bords(onde w);
void limites_onde_point(onde w, double t); 
void limites_mur_rect(onde w, int x1, int y1, int x2, int y2) ;
#endif
