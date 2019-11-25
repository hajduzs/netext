# NetExt

SIG compalition:

1. clone https://bitbucket.org/mkallmann/sig (results in a folder named sig on your path)

>sig applications only compile if they are placed in the same folder as the whole toolkit is. thats why if for example sig is under path/sig/, you'll nedd a folder at path/app/ to compile everything.

> install libglfw3-dev

2. navigate to sig/make/ and 
  2.1 extend the COPT variable with the -fPIC flag (important for the library)
  2.2 build the needed libs with 'make libs'

3. copy the makefile to path/app/make and the source to path/app/src

4. navigate to path/app/make, hit 'make' and use siglib.so as wanted



CGAL:

>install cmake

1. download and install cgal https://doc.cgal.org/latest/Manual/installation.html

2. create a temp directory: tmp/

3. copy the extracted json.hpp and dangerzone.cpp to tmp/

4. cgal_create_CMakeLists -s dangerzone.cpp

5. cmake .

6. make

7. use the 'dangerzone' application as wanted

*as wanted: copy the library and excetutable to the python projects libs/ folder and rename them according to the original filenames.
