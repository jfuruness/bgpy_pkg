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

### Personal modifications:
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Add a library using FindPython's tooling (pybind11 also provides a helper like
# this)
python_add_library(bgpc MODULE bgpc/src/main.cpp bgpc/src/announcement.cpp WITH_SOABI)

# Add the directory where the header files are located
target_include_directories(bgpc PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/bgpc/include)

target_link_libraries(bgpc PRIVATE pybind11::headers)

# This is passing in the version as a define just as an example
target_compile_definitions(bgpc PRIVATE VERSION_INFO=${PROJECT_VERSION})

# The install directory is the output (wheel) directory
install(TARGETS bgpc DESTINATION bgpy)
