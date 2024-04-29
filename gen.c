#include <stdio.h>
#include <math.h>
#include <stdbool.h>

double val(double x, double y, double t) {
     return sin(0.02*x + 0.05*y - 2.5*t) + 0.3*cos(0.2*x - 0.25*y - 8.5*t);
}

void output(double t) {
    for (int i=0; i<200; ++i) {
        for (int j=0; j<200; ++j) {
            if (j) { printf(","); }
            printf("%.2lf", val(i, j, t));
        }
        printf("\n");
    }
}

int main(void) {
    double t = 0.0;
    while (true) {
        output(t);
        t += 0.05;
    }
}
