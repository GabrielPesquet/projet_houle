CFLAGS= -Wall -pedantic
LDFLAGS= 

.PHONY= clean mrproper calc show run

houle.o: houle.c
	gcc $(CFLAGS) -c houle.c -lSDL2 -lm

houle: houle.o
	gcc $(LDFLAGS) -o houle houle.o -lm -lSDL2 -lm

calc: houle
	./houle

show: data.bin
	python3 grapher.py 

run : calc show

clean:
	rm -f *.o core

mrproper: clean
	rm -f houle 
	rm -f data.bin
