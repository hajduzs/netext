# DEPENDENCIES:
# libcgal-dev
# libglfw3-dev

# PROGRAMS NEEDED:
# make
# cmake
# curl

# SIG INSTALLATION AND SO COMPILATION

mkdir build
cd build

git clone https://bitbucket.org/mkallmann/sig
sed '12s/$/ -fPIC/' sig/make/makefile > mf2.txt
# TODO: a method has defaults in header, thus a lib is not compiling.
# fix this issue, because pull requests are not permitted
mv mf2.txt sig/make/makefile

cd sig/make
make libs

cd ../..
mkdir siglib
cd siglib
mkdir make
mkdir src

cp ../../libs/sources/sig_makefile make/makefile
cp ../../libs/sources/rdetours.cpp src/rdetours.cpp

cd make
make

cp siglib.so ../../../libs/siglib.so

cd ../..

# CGAL INSTALL 

mkdir cgallib
cd cgallib

curl -O https://raw.githubusercontent.com/nlohmann/json/develop/single_include/nlohmann/json.hpp
cp ../../libs/sources/dangerzone.cpp ./dangerzone.cpp
cp ../../libs/sources/CMakeLists.txt ./CMakeLists.txt

cmake .
make

# cp libpartition.so ../../libs/libpartition.so
cp dangerzone ../../libs/partitioner.x