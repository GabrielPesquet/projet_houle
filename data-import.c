#include <stdio.h>
#include <stdlib.h>
#include <netcdf.h>
#include "data-import.h"

#define FILE_NAME "brest.nc"
#define LAT_NAME "latitude"
#define LON_NAME "longitude"
#define ELEV_NAME "elevation"

// Gestion des erreurs NetCDF
#define NC_CHECK(status) { if (status != NC_NOERR) { printf("Erreur NetCDF: %s\n", nc_strerror(status)); exit(1); } }

float** get_elevations() {
    int ncid, lat_varid, lon_varid, elev_varid;
    size_t lat_len, lon_len;

    // Ouvrir le fichier NetCDF
    int status = nc_open(FILE_NAME, NC_NOWRITE, &ncid);
    NC_CHECK(status);

    // Obtenir les IDs des variables
    status = nc_inq_varid(ncid, LAT_NAME, &lat_varid);
    NC_CHECK(status);
    status = nc_inq_varid(ncid, LON_NAME, &lon_varid);
    NC_CHECK(status);
    status = nc_inq_varid(ncid, ELEV_NAME, &elev_varid);
    NC_CHECK(status);

    // Obtenir les IDs des dimensions
    int lat_dimid, lon_dimid;
    status = nc_inq_dimid(ncid, LAT_NAME, &lat_dimid);
    NC_CHECK(status);
    status = nc_inq_dimid(ncid, LON_NAME, &lon_dimid);
    NC_CHECK(status);

    // Obtenir les longueurs des dimensions
    status = nc_inq_dimlen(ncid, lat_dimid, &lat_len);
    NC_CHECK(status);
    status = nc_inq_dimlen(ncid, lon_dimid, &lon_len);
    NC_CHECK(status);

    // Allouer la mémoire pour les variables
    float *lat = (float*) malloc(lat_len * sizeof(float));
    float *lon = (float*) malloc(lon_len * sizeof(float));
    float **elevation = (float**) malloc(lat_len * sizeof(float*));
    for (size_t i = 0; i < lat_len; i++) {
        elevation[i] = (float*) malloc(lon_len * sizeof(float));
    }

    // Lire les données des variables
    status = nc_get_var_float(ncid, lat_varid, lat);
    NC_CHECK(status);
    status = nc_get_var_float(ncid, lon_varid, lon);
    NC_CHECK(status);
    float *elev_data = (float*) malloc(lat_len * lon_len * sizeof(float));
    status = nc_get_var_float(ncid, elev_varid, elev_data);
    NC_CHECK(status);

    // Organiser les données d'élévation dans une matrice 2D
    for (size_t i = 0; i < lat_len; i++) {
        for (size_t j = 0; j < lon_len; j++) {
            elevation[i][j] = elev_data[i * lon_len + j];
        }
    }

    // Afficher quelques valeurs (pour vérifier)
    printf("Latitudes: ");
    for (size_t i = 0; i < 5; i++) {
        printf("%f ", lat[i]);
    }
    printf("\nLongitudes: ");
    for (size_t i = 0; i < 5; i++) {
        printf("%f ", lon[i]);
    }
    printf("\nElevations: ");
    for (size_t i = 0; i < 5; i++) {
        for (size_t j = 0; j < 5; j++) {
            printf("%f ", elevation[i][j]);
        }
        printf("\n");
    }

    // Fermer le fichier NetCDF
    status = nc_close(ncid);
    NC_CHECK(status);

    // Libérer la mémoire allouée
    free(lat);
    free(lon);
    free(elev_data);
    for (size_t i = 0; i < lat_len; i++) {
        free(elevation[i]);
    }

    // Je crois que c'est la latitude puis la longitude
    printf("Elevation shape : (%ld, %ld)", lat_len, lon_len);
    //free(elevation);
    return elevation;
}

int three(){
    return 3;
}