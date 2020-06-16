cd ../../cgallib
cp ../../libs/sources/dangerzone.cpp ./dangerzone.cpp
cp ../../libs/sources/CMakeLists.txt ./CMakeLists.txt
cmake .
make
cp dangerzone ../../libs/partitioner.x