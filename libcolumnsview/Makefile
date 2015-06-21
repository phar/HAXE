all:
	g++ -c -fPIC -I/usr/include/qt4 -I. -lQtGui *.cpp
	gcc -shared -lQtGui -Wl,-soname,libcolumnsview.so -o libcolumnsview.so *.o
clean:
	rm -f *.so *.o
