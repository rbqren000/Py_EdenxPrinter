# MX Printer SDK 示例程序 CMakeLists.txt
# 作者: RBQ
# 版本: 1.0.0
# 日期: 2025

cmake_minimum_required(VERSION 3.16)
project(MXPrinterExamples VERSION 1.0.0 LANGUAGES C CXX)

# 设置C/C++标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找MX Printer SDK
find_package(MXPrinter REQUIRED)

if(NOT MXPrinter_FOUND)
    message(FATAL_ERROR "MX Printer SDK not found. Please install the SDK first.")
endif()

message(STATUS "Found MX Printer SDK")
message(STATUS "  Version: ${MXPrinter_VERSION}")
message(STATUS "  Include dirs: ${MXPrinter_INCLUDE_DIRS}")
message(STATUS "  Libraries: ${MXPrinter_LIBRARIES}")

# 包含头文件目录
include_directories(${MXPrinter_INCLUDE_DIRS})

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# C语言示例
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/c/basic_usage.c")
    add_executable(mx_basic_usage_c
        c/basic_usage.c
    )
    
    target_link_libraries(mx_basic_usage_c
        ${MXPrinter_LIBRARIES}
    )
    
    # 设置目标属性
    set_target_properties(mx_basic_usage_c PROPERTIES
        OUTPUT_NAME "mx_basic_usage_c"
        C_STANDARD 11
        C_STANDARD_REQUIRED ON
    )
    
    message(STATUS "Added C example: mx_basic_usage_c")
else()
    message(WARNING "C example source file not found: c/basic_usage.c")
endif()

# C++语言示例
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cpp/printer_manager.cpp")
    add_executable(mx_printer_manager_cpp
        cpp/printer_manager.cpp
    )
    
    target_link_libraries(mx_printer_manager_cpp
        ${MXPrinter_LIBRARIES}
    )
    
    # 设置目标属性
    set_target_properties(mx_printer_manager_cpp PROPERTIES
        OUTPUT_NAME "mx_printer_manager_cpp"
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
    )
    
    message(STATUS "Added C++ example: mx_printer_manager_cpp")
else()
    message(WARNING "C++ example source file not found: cpp/printer_manager.cpp")
endif()

# 安装示例程序
if(TARGET mx_basic_usage_c)
    install(TARGETS mx_basic_usage_c
        RUNTIME DESTINATION bin/examples
        COMPONENT Examples
    )
endif()

if(TARGET mx_printer_manager_cpp)
    install(TARGETS mx_printer_manager_cpp
        RUNTIME DESTINATION bin/examples
        COMPONENT Examples
    )
endif()

# 安装Python示例
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/python/mx_printer_demo.py")
    install(FILES python/mx_printer_demo.py
        DESTINATION share/mx_printer/examples/python
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                   GROUP_READ GROUP_EXECUTE
                   WORLD_READ WORLD_EXECUTE
        COMPONENT Examples
    )
    message(STATUS "Added Python example: mx_printer_demo.py")
else()
    message(WARNING "Python example source file not found: python/mx_printer_demo.py")
endif()

# 创建示例文档
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
    install(FILES README.md
        DESTINATION share/mx_printer/examples
        COMPONENT Examples
    )
else()
    # 如果没有README.md，创建一个简单的说明文件
    file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/README.txt"
        "MX Printer SDK Examples\n"
        "========================\n\n"
        "This directory contains example programs for the MX Printer SDK.\n\n"
        "C Examples:\n"
        "  - mx_basic_usage_c: Basic C API usage demonstration\n\n"
        "C++ Examples:\n"
        "  - mx_printer_manager_cpp: Object-oriented C++ wrapper demonstration\n\n"
        "Python Examples:\n"
        "  - mx_printer_demo.py: Python SDK usage demonstration\n\n"
        "To run the examples, make sure the MX Printer SDK is properly installed.\n"
    )
    
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/README.txt"
        DESTINATION share/mx_printer/examples
        COMPONENT Examples
    )
endif()

# 打印构建信息
message(STATUS "")
message(STATUS "MX Printer SDK Examples Configuration:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C compiler: ${CMAKE_C_COMPILER}")
message(STATUS "  C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "  Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "  Examples will be installed to: ${CMAKE_INSTALL_PREFIX}/bin/examples")
message(STATUS "  Python examples will be installed to: ${CMAKE_INSTALL_PREFIX}/share/mx_printer/examples/python")
message(STATUS "")

# 添加自定义目标来运行示例
if(TARGET mx_basic_usage_c)
    add_custom_target(run_c_example
        COMMAND mx_basic_usage_c
        DEPENDS mx_basic_usage_c
        WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
        COMMENT "Running C example"
    )
endif()

if(TARGET mx_printer_manager_cpp)
    add_custom_target(run_cpp_example
        COMMAND mx_printer_manager_cpp
        DEPENDS mx_printer_manager_cpp
        WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
        COMMENT "Running C++ example"
    )
endif()

# Python示例运行目标
find_program(PYTHON_EXECUTABLE python3 python)
if(PYTHON_EXECUTABLE AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/python/mx_printer_demo.py")
    add_custom_target(run_python_example
        COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/python/mx_printer_demo.py"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python
        COMMENT "Running Python example"
    )
endif()

# 运行所有示例的目标
add_custom_target(run_all_examples
    COMMENT "Running all examples"
)

if(TARGET run_c_example)
    add_dependencies(run_all_examples run_c_example)
endif()

if(TARGET run_cpp_example)
    add_dependencies(run_all_examples run_cpp_example)
endif()

if(TARGET run_python_example)
    add_dependencies(run_all_examples run_python_example)
endif()