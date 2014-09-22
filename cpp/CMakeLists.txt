cmake_minimum_required(VERSION 2.8)

project(thesis CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR})
find_package(ACADO REQUIRED)

include_directories(. ${ACADO_INCLUDE_DIRS})
add_executable(thesis test.cpp)
target_link_libraries(thesis ${ACADO_SHARED_LIBRARIES})
set_target_properties(thesis PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
