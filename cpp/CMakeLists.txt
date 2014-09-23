cmake_minimum_required(VERSION 2.8)

project(thesis CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR})
find_package(ACADO REQUIRED)

include_directories(. ${ACADO_INCLUDE_DIRS})

# Test integrator
add_executable(test test.cpp)
target_link_libraries(test ${ACADO_SHARED_LIBRARIES})
