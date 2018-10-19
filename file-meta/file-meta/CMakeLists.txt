cmake_minimum_required(VERSION 3.0.2)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/install" CACHE PATH "Default install prefix") 

set(PROJECT_NAME "file-meta")
project(${PROJECT_NAME})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

enable_testing()

file(GLOB_RECURSE project_SRC src/*.cpp)
list(REMOVE_ITEM project_SRC EXCLUDE src/main.cpp)
file(GLOB_RECURSE project_MAIN src/main.cpp)

set(project_INCLUDE_DIR ${CMAKE_CURRENT_LIST_DIR}/include)

set(CMAKE_CXX_STANDARD 11)

if (BUILD_SHARED_LIBS)
	add_library(hashes SHARED ${project_SRC})
	target_include_directories(hashes PRIVATE ${project_INCLUDE_DIR})
	target_link_libraries(hashes PRIVATE ${CONAN_LIBS_GFLAGS} ${CONAN_LIBS_OPENSSL} ${CONAN_LIBS_BOOST})
endif()

add_library(hashesstatic STATIC ${project_SRC})
target_include_directories(hashesstatic PRIVATE ${project_INCLUDE_DIR})
target_link_libraries(hashesstatic PRIVATE ${CONAN_LIBS_GFLAGS} ${CONAN_LIBS_OPENSSL} ${CONAN_LIBS_BOOST})

add_executable(compute-hashes ${project_MAIN})
target_include_directories(compute-hashes PRIVATE ${project_INCLUDE_DIR})
target_link_libraries(compute-hashes PRIVATE hashesstatic ${CONAN_LIBS_LIBCURL})

if (NOT DEFINED CMAKE_INSTALL_BINDIR)
	set(CMAKE_INSTALL_BINDIR "${CMAKE_INSTALL_PREFIX}/bin")
endif()
if (NOT DEFINED CMAKE_INSTALL_INCLUDEDIR)
	set(CMAKE_INSTALL_INCLUDEDIR "${CMAKE_INSTALL_PREFIX}/include")
endif()
if (NOT DEFINED CMAKE_INSTALL_LIBDIR)
	set(CMAKE_INSTALL_LIBDIR "${CMAKE_INSTALL_PREFIX}/lib")
endif()

if (BUILD_SHARED_LIBS)
	install(TARGETS hashes
		INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
		RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
		LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
		ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
	install(TARGETS hashes DESTINATION lib)
endif()

install(TARGETS hashesstatic compute-hashes
	INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
	RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
	LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
	ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(TARGETS hashesstatic DESTINATION lib)
