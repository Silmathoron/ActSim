# Specify the version being used aswell as the language
cmake_minimum_required(VERSION 2.6)
# Name your project here
project(simulator)

# Get libraries
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

#find_package(MPI REQUIRED)
#include_directories(${MPI_INCLUDE_PATH})

find_package(Boost 1.58.0 COMPONENTS python system REQUIRED)
set(Boost_INCLUDE_DIR /usr/local/include)
include_directories(${Boost_INCLUDE_DIRS})

find_package(OpenCL)
include_directories(${OPENCL_INCLUDE_DIR})

set(vexCL_INCLUDE_DIR /usr/include/vexcl)
include_directories(${vexCL_INCLUDE_DIR})

#Sends the flags to the compiler
add_definitions(-std=c++11 -g3)

# Sources and headers
set(SOURCES activitySimulator.cpp tools/convertor.cpp)
set(HEADER_FILES activitySimulator.hpp tools/convertor.hpp)

# Make the program
add_library(simulator SHARED ${SOURCES} ${HEADER_FILES})
target_link_libraries(simulator ${Boost_LIBRARIES} ${PYTHON_LIBRARIES} ${OPENCL_LIBRARIES})
