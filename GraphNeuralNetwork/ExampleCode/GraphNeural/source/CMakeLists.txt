cmake_minimum_required( VERSION 3.2 FATAL_ERROR )

project( GraphNeural )

set(CMAKE CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)
find_package(ROOT REQUIRED COMPONENTS Core Tree tensorflow)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(GraphNeural)
include_directories(Root)

file(GLOB GraphLibs GraphNeural/*.h Root/*.cxx)

add_executable( GraphNeural util/GraphNeural.cxx ${GraphLibs})
target_link_libraries(GraphNeural PUBLIC ROOT::Tree)
