CFLAGS= -Wall -pedantic
LDFLAGS= 

.PHONY= clean mrproper calc show run

houle.o: houle.h houle.c
	gcc $(CFLAGS) -c houle.c

config.o: config.h config.c 
	gcc $(CFLAGS) -c config.c 

houle: houle.o config.o
	gcc $(LDFLAGS) -o houle houle.o config.o -lm

calc: houle
	./houle

show:
	python3 grapher.py 

run : houle
	./houle | python3 disp.py	

clean:
	rm -f *.o core

mrproper: clean
	rm -f houle 
	rm -f data.bin
