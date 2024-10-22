CFLAGS= -Wall -pedantic
LDFLAGS= 

.PHONY= clean mrproper calc show run

houle.o: houle.c
	gcc $(CFLAGS) -c houle.c

houle: houle.o
	gcc $(LDFLAGS) -o houle houle.o -lm

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
