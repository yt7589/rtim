cmake_minimum_required(VERSION 3.10)
project(generate_test_surface)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# # find_package(OpenCASCADE REQUIRED)
# # set (OpenCASCADE_LIBRARIES "/home/yantao/opencascade/lib")
# # 1. 首先查找PkgConfig模块
# find_package(PkgConfig REQUIRED)
# # 或者直接指定pc文件路径
# set(PKG_CONFIG_PATH "/home/yantao/opencascade/lib/pkgconfig:${PKG_CONFIG_PATH}")
# pkg_check_modules(OCC REQUIRED opencascade)
# # find_package(OpenCASCADE REQUIRED)
# # 使用 pkg_check_modules - 这里的 "OCC" 是前缀

# # 调试输出，查看实际获得的变量
# message(STATUS "=== pkg_check_modules 输出 ===")
# message(STATUS "OCC_FOUND: ${OCC_FOUND}")
# message(STATUS "OCC_VERSION: ${OCC_VERSION}")
# message(STATUS "OCC_INCLUDE_DIRS: ${OCC_INCLUDE_DIRS}")
# message(STATUS "OCC_LIBRARY_DIRS: ${OCC_LIBRARY_DIRS}")
# message(STATUS "OCC_LIBRARIES: ${OCC_LIBRARIES}")
# message(STATUS "OCC_LDFLAGS: ${OCC_LDFLAGS}")
# message(STATUS "OCC_CFLAGS: ${OCC_CFLAGS}")
# message(STATUS "OCC_CFLAGS_OTHER: ${OCC_CFLAGS_OTHER}")



set(OpenCASCADE_DIR "/home/yantao/opencascade/lib/cmake/opencascade")
find_package(OpenCASCADE REQUIRED)

# 或者使用 pkg-config
find_package(PkgConfig REQUIRED)
pkg_check_modules(OCC REQUIRED opencascade)
include_directories(${OCC_INCLUDE_DIRS})

include_directories(${OCC_INCLUDE_DIRS})
link_directories(${OCC_LIBRARY_DIRS})

message (STATUS "${OCC_LIBRARIES}??????????????")


add_executable(generate_test_surface generate_test_surface.cpp)
target_link_libraries(generate_test_surface ${OCC_LIBRARIES})