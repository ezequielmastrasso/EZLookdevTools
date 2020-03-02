set(SOURCE_FILES
    "__init_.py"
)

#set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIRECTORY}/modules)
find_package(Maya REQUIRED)

include_directories(${MAYA_INCLUDE_DIR})
link_directories(${MAYA_LIBRARY_DIR})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES})

MAYA_PLUGIN(${PROJECT_NAME})