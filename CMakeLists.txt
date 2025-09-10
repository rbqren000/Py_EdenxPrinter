cmake_minimum_required(VERSION 3.16)
project(MXPrinter VERSION 1.0.0 LANGUAGES C CXX)

# 设置C/C++标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置编译选项
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 平台检测
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(TARGET_PLATFORM "windows")
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "AMD64|x86_64")
        set(TARGET_ARCH "x64")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "ARM64|aarch64")
        set(TARGET_ARCH "arm64")
    else()
        set(TARGET_ARCH "x86")
    endif()
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(TARGET_PLATFORM "macos")
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64")
        set(TARGET_ARCH "arm64")
    else()
        set(TARGET_ARCH "x86_64")
    endif()
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(TARGET_PLATFORM "linux")
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
        set(TARGET_ARCH "arm64")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm")
        set(TARGET_ARCH "armv7")
    else()
        set(TARGET_ARCH "x86_64")
    endif()
else()
    set(TARGET_PLATFORM "unknown")
    set(TARGET_ARCH "unknown")
endif()

message(STATUS "Target Platform: ${TARGET_PLATFORM}")
message(STATUS "Target Architecture: ${TARGET_ARCH}")

# 可选：构建C语言SDK
option(BUILD_C_SDK "Build C language SDK (mx_printer)" OFF)

# SDK源文件
set(SDK_SOURCES
    sdk/src/mx_printer.c
)

# 仅在启用BUILD_C_SDK选项时构建C语言SDK
if(BUILD_C_SDK)
    message(STATUS "C language SDK (mx_printer) will be built")
    
    # 创建静态库
    add_library(mx_printer_static STATIC ${SDK_SOURCES})
    target_include_directories(mx_printer_static PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/sdk/include>
        $<INSTALL_INTERFACE:include>
    )

    # 创建动态库
    add_library(mx_printer_shared SHARED ${SDK_SOURCES})
    target_include_directories(mx_printer_shared PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/sdk/include>
        $<INSTALL_INTERFACE:include>
    )

    # 设置库的输出名称
    set_target_properties(mx_printer_static PROPERTIES OUTPUT_NAME mx_printer)
    set_target_properties(mx_printer_shared PROPERTIES OUTPUT_NAME mx_printer)

    # 平台特定设置
    if(TARGET_PLATFORM STREQUAL "windows")
        # Windows特定设置
        target_compile_definitions(mx_printer_static PRIVATE MX_WINDOWS=1)
        target_compile_definitions(mx_printer_shared PRIVATE MX_WINDOWS=1)
        
        # 导出符号
        target_compile_definitions(mx_printer_shared PRIVATE MX_EXPORTS)
        
    elseif(TARGET_PLATFORM STREQUAL "macos")
        # macOS特定设置
        target_compile_definitions(mx_printer_static PRIVATE MX_MACOS=1)
        target_compile_definitions(mx_printer_shared PRIVATE MX_MACOS=1)
        
        # 查找系统框架
        find_library(COREFOUNDATION_FRAMEWORK CoreFoundation)
        find_library(IOKIT_FRAMEWORK IOKit)
        
        if(COREFOUNDATION_FRAMEWORK AND IOKIT_FRAMEWORK)
            target_link_libraries(mx_printer_static ${COREFOUNDATION_FRAMEWORK} ${IOKIT_FRAMEWORK})
            target_link_libraries(mx_printer_shared ${COREFOUNDATION_FRAMEWORK} ${IOKIT_FRAMEWORK})
        endif()
        
    elseif(TARGET_PLATFORM STREQUAL "linux")
        # Linux特定设置
        target_compile_definitions(mx_printer_static PRIVATE MX_LINUX=1)
        target_compile_definitions(mx_printer_shared PRIVATE MX_LINUX=1)
        
        # 链接系统库
        target_link_libraries(mx_printer_static pthread)
        target_link_libraries(mx_printer_shared pthread)
    endif()

    # 安装配置
    install(TARGETS mx_printer_static mx_printer_shared
        EXPORT MXPrinterTargets
        LIBRARY DESTINATION lib/${TARGET_PLATFORM}/${TARGET_ARCH}
        ARCHIVE DESTINATION lib/${TARGET_PLATFORM}/${TARGET_ARCH}
        RUNTIME DESTINATION bin/${TARGET_PLATFORM}/${TARGET_ARCH}
    )

    # 安装头文件
    install(FILES sdk/include/mx_printer.h
        DESTINATION include
    )
else()
    message(STATUS "C language SDK (mx_printer) will not be built")
endif()

# 创建配置文件
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/MXPrinterConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

# 仅在启用BUILD_C_SDK选项时导出C语言SDK目标
if(BUILD_C_SDK)
    # 导出目标
    install(EXPORT MXPrinterTargets
        FILE MXPrinterTargets.cmake
        NAMESPACE MXPrinter::
        DESTINATION lib/cmake/MXPrinter
    )
endif()

# 配置文件
configure_file(
    "${CMAKE_SOURCE_DIR}/cmake/MXPrinterConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/MXPrinterConfig.cmake"
    @ONLY
)

# 安装配置文件
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/MXPrinterConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/MXPrinterConfigVersion.cmake"
    DESTINATION lib/cmake/MXPrinter
)

# 可选：构建示例和测试
option(BUILD_EXAMPLES "Build examples" OFF)
option(BUILD_TESTS "Build tests" OFF)

if(BUILD_EXAMPLES)
    message(STATUS "Examples will be built")
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/examples/CMakeLists.txt")
        add_subdirectory(examples)
    else()
        message(WARNING "Examples directory not found")
    endif()
endif()

if(BUILD_TESTS)
    message(STATUS "Tests will be built")
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/CMakeLists.txt")
        add_subdirectory(tests)
    else()
        message(WARNING "Tests directory not found")
    endif()
endif()

# 打印构建信息
message(STATUS "")
message(STATUS "MX Printer SDK Configuration:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Platform: ${TARGET_PLATFORM}")
message(STATUS "  Architecture: ${TARGET_ARCH}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Install Prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")