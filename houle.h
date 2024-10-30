#ifndef HOULE_H
#define HOULE_H
#include <math.h>
#include <stdlib.h>

#define pi 3.141592  
#define g 9.81 

typedef struct Onde
{
	double lambda;
	double ***champ; // trois dimensions temps (3) x (XMAX) y (YMAX)
} onde;

onde new_onde(double longueur_onde); 

double sq(double x); // square 

void update_h(double t) ; // change la hauteur d'eau 
void update_onde(onde w, double t); // controle evolution de l'onde globale
void futur_onde(onde w, int x , int y) ; // controle local
double calc_c(double lambda, int x, int y); // calcul de la célérité de l'onde 
double laplacien(double ** champ, int x, int y); 

void limites(double t) ; // conditions globales des limites sur les ondes, ne rentrant pas d'ED autonome.   
void init() ; // initialisation du fond marin, et des ondes à t = 0 

#endif
