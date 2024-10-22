CFLAGS= -Wall -pedantic
LDFLAGS= 
NCFLAGS = $(shell nc-config --cflags --libs)

.PHONY= clean mrproper calc show run

houle.o: houle.c
	gcc $(CFLAGS) -c houle.c 

data-import.o : data-import.c
	gcc $(CFLAGS) -c data-import.c $(nc-config --cflags --libs)

houle: houle.o data-import.o
	gcc $(LDFLAGS) -o houle houle.o data-import.o -lm $(NCFLAGS)

calc: houle
	./houle

show: data.bin
	python3 grapher.py 

run : houle 
	./houle | python3 disp.py	

clean:
	rm -f *.o core

mrproper: clean
	rm -f houle 
	rm -f data.bin
