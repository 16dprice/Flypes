// gcc example.c -o example -lm -lplCurve -lgsl -g3

#include<stdio.h>
#include<stdbool.h>
#include<string.h>
#include<stdint.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>
#include<assert.h>
#include<limits.h>
#include<inttypes.h>

#include"plcTopology.h"

/* We use a local, compiled in copy of argtable to avoid having to
   depend on system utilities. */

int PD_VERBOSE = 0; // some of the library functions check for this (sets level of error debugging)
int VERBOSE;


/**

The file path will be given as the first argument to this script. !!THIS IS EXPECTED AND THE PROGRAM WILL TERMINATE
IF IT IS NOT GIVEN!! If an input file name is provided, it will be the second argument to the script. If not,
we default to 'pdcodes.txt'. If an input file name is provided, then an output name may or may not be provided.
If it is, then it will be the third argument. If it is not, we default to 'reduced_codes.txt' and 'reduced_codes.pdstor'.
It should be kept in mind that the way we are taking input, there is no way to reasonably give an output file name
while excluding an input file name. Thus, there is no way to use the default input file name while using a custom
output file name.

*/
int main(int argc, char *argv[]) {

	// variables

	pd_stor_t *flype_circuit;
	FILE *infile, *outfile;
	pd_code_t *next_pd_code;
	int i;
	long imax;
	char line[1000]; // set this and len to really big numbers because this dictates the max length of a line we can read
	size_t len = 1000;
	ssize_t read;
	char *endptr;

	char infile_path[100]; // there's no way the path will be over 100 characters... I really hope
	char infile_full_path[150]; // same here...
	char outfile_path[100];
	char outfile_full_txt_path[150]; // path for the output txt file
	char outfile_full_pdstor_path[150]; // path for the output pdstor file

	// end variables

	if(argc < 2) {
//	    printf("Not enough arguments supplied.\n");
	    return(-1);
	} else {

        // copy the file path to the input file path and then append the input file name to it
        strcpy(infile_path, argv[1]);
        strcpy(infile_full_path, strcat(infile_path, "pdcodes.txt"));

        // same as above but for output file
        // actually need two though, one for the output txt file and one for the output pdstor file
        strcpy(outfile_path, argv[1]);
        strcpy(outfile_full_txt_path, strcat(outfile_path, "reduced_codes.txt"));

        strcpy(outfile_path, argv[1]);
        strcpy(outfile_full_pdstor_path, strcat(outfile_path, "reduced_codes.pdstor"));

	}
//    printf("here\n");
	// some declarations
	flype_circuit = pd_new_pdstor();
	infile = fopen(infile_full_path, "r"); // example file

	// iterate through until read is the first line with length not equal to 1
	// this will be the number of pd codes contained in the file
	while(strlen(fgets(line, len, infile)) == 1) {}

	imax = strtol(line, &endptr, 10);

//	printf("imax is %ld\n", imax);

	for(i=0; i < imax; i++) {
		// get the next pd code from the file
		// TODO: what to do if this is null???
		next_pd_code = pd_read_KnotTheory(infile);
//        printf("done with pd code %d\n", i + 1);
		// add the pd code to the flype_circuit
		pd_addto_pdstor(flype_circuit, next_pd_code, DIAGRAM_ISOTOPY);

		// because no garbage collection
		free(next_pd_code);
	}
//	printf("DONE READING PD CODES\n");

	outfile = fopen(outfile_full_pdstor_path, "w");
	pd_write_pdstor(outfile, flype_circuit);
//	printf("here2\n");
	fclose(outfile);
//	printf("DONE WRITING TO FILE\n");

	outfile = fopen(outfile_full_txt_path, "w");
	for(next_pd_code = pd_stor_firstelt(flype_circuit); next_pd_code != NULL; next_pd_code = pd_stor_nextelt(flype_circuit)) {

		pd_write_KnotTheory(outfile, next_pd_code);
		free(next_pd_code);
	}

	fclose(outfile);

	// free everything
	pd_free_pdstor(&flype_circuit);

	return(0);
}
