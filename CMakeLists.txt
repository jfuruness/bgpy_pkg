# Mostly used from: https://github.com/pybind/scikit_build_example
# basically the only example I could find using cmake from a pip install
# (rather than others which required a git clone)


# Require CMake 3.15+ (matching scikit-build-core) Use new versions of all
# policies up to CMake 3.27
cmake_minimum_required(VERSION 3.15...3.27)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX)

### Personal modifications##############################
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Set the default build type to Release if not specified
#if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
#endif()
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native")

################################################################

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

##################modification
# Check for LTO support and enable it if possible
include(CheckIPOSupported)
check_ipo_supported(RESULT lto_supported)
if(lto_supported)
  message(STATUS "LTO supported")
else()
  message(STATUS "LTO not supported")
endif()
#####################################


# Add a library using FindPython's tooling (pybind11 also provides a helper like
# this)
############################################################################
# Automatically include all .cpp files in bgpc/src and its subdirectories
# file(GLOB_RECURSE BGPC_SOURCES "bgpc/src/*.cpp")
# python_add_library(bgpc MODULE bgpc/src/main.cpp bgpc/src/announcement.cpp bgpc/src/ann_containers/local_rib.cpp WITH_SOABI)
# python_add_library(bgpc MODULE ${BGPC_SOURCES} WITH_SOABI)

set(BGPC_SOURCES
    bgpc/src/cpp_simulation_engine/announcement.cpp
    bgpc/src/cpp_simulation_engine/ann_containers/local_rib.cpp
    bgpc/src/cpp_simulation_engine/ann_containers/recv_queue.cpp
    bgpc/src/cpp_simulation_engine/policies/policy.cpp
    bgpc/src/cpp_simulation_engine/policies/bgp_simple_policy/bgp_simple_policy.cpp
    bgpc/src/cpp_simulation_engine/policies/bgp_simple_policy/gao_rexford_funcs.cpp
    bgpc/src/cpp_simulation_engine/policies/bgp_simple_policy/process_incoming_funcs.cpp
    bgpc/src/cpp_simulation_engine/policies/bgp_simple_policy/propagate_funcs.cpp
    bgpc/src/as_graph/as.cpp
    bgpc/src/as_graph/as_graph.cpp
    bgpc/src/cpp_simulation_engine/cpp_simulation_engine.cpp
    bgpc/src/utils.cpp
    bgpc/src/main.cpp
)

python_add_library(bgpc MODULE ${BGPC_SOURCES} WITH_SOABI)
##############################################################################

########################modification
if(lto_supported)
  set_property(TARGET bgpc PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()
####################################

# Add the directory where the header files are located
# Also include the new directory for ann_containers
# Old way:
# target_include_directories(bgpc PRIVATE
#   ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include
#   ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/ann_containers
# )
#######################################################################
# New Way:
# Get all subdirectories in bgpc/include
# file(GLOB children RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/*)
# set(include_dirs "")
# foreach(child ${children})
#     if(IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/${child})
#         list(APPEND include_dirs ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/${child})
#     endif()
# endforeach()

# Print out include directories for debugging
# foreach(dir ${include_dirs})
#     message(STATUS "Including directory: ${dir}")
# endforeach()

# Now include these directories
# target_include_directories(bgpc PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include ${include_dirs})

# Going back to og

# Manually include directories
target_include_directories(bgpc PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include
    ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/cpp_simulation_engine/ann_containers
    ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/cpp_simulation_engine/policies
    ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/as_graph
    ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include/cpp_simulation_engine
)
######################################################################

target_link_libraries(bgpc PRIVATE pybind11::headers)

# This is passing in the version as a define just as an example
target_compile_definitions(bgpc PRIVATE VERSION_INFO=${PROJECT_VERSION})

# The install directory is the output (wheel) directory
install(TARGETS bgpc DESTINATION bgpy)
