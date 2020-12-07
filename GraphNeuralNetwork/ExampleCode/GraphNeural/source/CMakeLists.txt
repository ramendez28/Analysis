cmake_minimum_required( VERSION 3.2 FATAL_ERROR )

project( GraphNeural )

set(CMAKE_CXX_STANDARD_REQUIRED True)

#Find the ROOT libraries and include them 
find_package(ROOT REQUIRED COMPONENTS Core Tree)

#Find PyTorch. To include this you need to run cmake ../source/ -DCMAKE_PREFIX_PATH=directory to pyTorch  
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")


# Define the directories we are going to use in this build project 
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(GraphNeural)
include_directories(Root)
file(GLOB GraphLibs GraphNeural/*.h Root/*.cxx)


add_executable( GraphNeural util/GraphNeural.cxx ${GraphLibs})
target_link_libraries(GraphNeural PUBLIC ROOT::Tree "${TORCH_LIBRARIES}")
set_property(TARGET GraphNeural PROPERTY CXX_STANDARD 14)

