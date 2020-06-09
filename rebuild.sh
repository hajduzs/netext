cd build
cd siglib
cp ../../libs/sources/rdetours.cpp src/rdetours.cpp
cd make
make
cp siglib.so ../../../libs/siglib.so

cd ../../cgallib
cp ../../libs/sources/dangerzone.cpp ./dangerzone.cpp
cp ../../libs/sources/CMakeLists.txt ./CMakeLists.txt
cmake .
make
cp dangerzone ../../libs/partitioner.x