# NetExt

SIG compalition:

1. clone https://bitbucket.org/mkallmann/sig (results in a folder named sig on your path)

>sig applications only compile if they are placed in the same folder as the whole toolkit is. thats why if for example sig is under path/sig/, you'll nedd a folder at path/app/ to compile everything.

2. navigate to sig/make/ and build the needed libs with 'make'

3. copy the makefile to path/app/make and the source to path/app/src

4. navigate to path/app/make, hit 'make' and use siglib.so as wanted




