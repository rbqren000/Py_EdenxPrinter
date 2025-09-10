# MX Printer SDK 测试套件 CMakeLists.txt
# 作者: RBQ
# 版本: 1.0.0
# 日期: 2025

cmake_minimum_required(VERSION 3.16)
project(MXPrinterTests VERSION 1.0.0 LANGUAGES C CXX)

# 设置C/C++标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
if(MSVC)
    add_compile_options(/W4)
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -g)
endif()

# 启用测试
enable_testing()

# 查找依赖
find_package(MXPrinter REQUIRED)

# 查找测试框架
find_package(GTest QUIET)
if(NOT GTest_FOUND)
    # 如果系统没有安装 GTest，尝试使用 FetchContent 下载
    include(FetchContent)
    
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.1
    )
    
    # 配置 GTest
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    set(BUILD_GMOCK ON CACHE BOOL "" FORCE)
    set(BUILD_GTEST ON CACHE BOOL "" FORCE)
    
    FetchContent_MakeAvailable(googletest)
    
    # 创建别名以保持一致性
    add_library(GTest::gtest ALIAS gtest)
    add_library(GTest::gtest_main ALIAS gtest_main)
    add_library(GTest::gmock ALIAS gmock)
    add_library(GTest::gmock_main ALIAS gmock_main)
    
    message(STATUS "Using FetchContent to download Google Test")
else()
    message(STATUS "Found Google Test: ${GTest_VERSION}")
endif()

# 包含头文件目录
include_directories(
    ${MXPrinter_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/tests)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 测试源文件列表
set(TEST_SOURCES
    test_mx_printer_basic.cpp
    test_mx_printer_devices.cpp
    test_mx_printer_image.cpp
    test_mx_printer_errors.cpp
)

# 创建测试源文件（如果不存在）
foreach(TEST_FILE ${TEST_SOURCES})
    if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}")
        message(STATUS "Creating test file: ${TEST_FILE}")
        
        if(TEST_FILE STREQUAL "test_mx_printer_basic.cpp")
            file(WRITE "${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}"
                "#include <gtest/gtest.h>\n"
                "#include \"mx_printer.h\"\n\n"
                "// 基础功能测试\n"
                "class MXPrinterBasicTest : public ::testing::Test {\n"
                "protected:\n"
                "    void SetUp() override {\n"
                "        handle = mx_init();\n"
                "    }\n\n"
                "    void TearDown() override {\n"
                "        if (handle) {\n"
                "            mx_cleanup(handle);\n"
                "        }\n"
                "    }\n\n"
                "    mx_handle_t handle = nullptr;\n"
                "};\n\n"
                "TEST_F(MXPrinterBasicTest, InitAndCleanup) {\n"
                "    EXPECT_NE(handle, nullptr);\n"
                "}\n\n"
                "TEST_F(MXPrinterBasicTest, GetVersion) {\n"
                "    const char* version = mx_get_version();\n"
                "    EXPECT_NE(version, nullptr);\n"
                "    EXPECT_GT(strlen(version), 0);\n"
                "}\n"
            )
        elseif(TEST_FILE STREQUAL "test_mx_printer_devices.cpp")
            file(WRITE "${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}"
                "#include <gtest/gtest.h>\n"
                "#include \"mx_printer.h\"\n\n"
                "// 设备管理测试\n"
                "class MXPrinterDeviceTest : public ::testing::Test {\n"
                "protected:\n"
                "    void SetUp() override {\n"
                "        handle = mx_init();\n"
                "        ASSERT_NE(handle, nullptr);\n"
                "    }\n\n"
                "    void TearDown() override {\n"
                "        if (handle) {\n"
                "            mx_cleanup(handle);\n"
                "        }\n"
                "    }\n\n"
                "    mx_handle_t handle = nullptr;\n"
                "};\n\n"
                "TEST_F(MXPrinterDeviceTest, ScanDevices) {\n"
                "    mx_device_info_t devices[10];\n"
                "    size_t device_count = 0;\n"
                "    mx_error_t result = mx_scan_devices(handle, devices, 10, &device_count);\n"
                "    EXPECT_EQ(result, MX_SUCCESS);\n"
                "}\n\n"
                "TEST_F(MXPrinterDeviceTest, ConnectInvalidDevice) {\n"
                "    mx_error_t result = mx_connect_device(handle, \"invalid_device_id\");\n"
                "    EXPECT_NE(result, MX_SUCCESS);\n"
                "}\n"
            )
        elseif(TEST_FILE STREQUAL "test_mx_printer_image.cpp")
            file(WRITE "${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}"
                "#include <gtest/gtest.h>\n"
                "#include \"mx_printer.h\"\n\n"
                "// 图像处理测试\n"
                "class MXPrinterImageTest : public ::testing::Test {\n"
                "protected:\n"
                "    void SetUp() override {\n"
                "        handle = mx_init();\n"
                "        ASSERT_NE(handle, nullptr);\n"
                "    }\n\n"
                "    void TearDown() override {\n"
                "        if (handle) {\n"
                "            mx_cleanup(handle);\n"
                "        }\n"
                "    }\n\n"
                "    mx_handle_t handle = nullptr;\n"
                "};\n\n"
                "TEST_F(MXPrinterImageTest, ProcessNonExistentImage) {\n"
                "    mx_image_params_t params = {};\n"
                "    mx_error_t result = mx_process_image(handle, \"non_existent.jpg\", \"output.jpg\", &params);\n"
                "    EXPECT_NE(result, MX_SUCCESS);\n"
                "}\n\n"
                "TEST_F(MXPrinterImageTest, GetImageInfoInvalidPath) {\n"
                "    mx_image_params_t info;\n"
                "    mx_error_t result = mx_get_image_info(handle, \"invalid_path.jpg\", &info);\n"
                "    EXPECT_NE(result, MX_SUCCESS);\n"
                "}\n"
            )
        elseif(TEST_FILE STREQUAL "test_mx_printer_errors.cpp")
            file(WRITE "${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}"
                "#include <gtest/gtest.h>\n"
                "#include \"mx_printer.h\"\n\n"
                "// 错误处理测试\n"
                "class MXPrinterErrorTest : public ::testing::Test {\n"
                "protected:\n"
                "    void SetUp() override {\n"
                "        handle = mx_init();\n"
                "        ASSERT_NE(handle, nullptr);\n"
                "    }\n\n"
                "    void TearDown() override {\n"
                "        if (handle) {\n"
                "            mx_cleanup(handle);\n"
                "        }\n"
                "    }\n\n"
                "    mx_handle_t handle = nullptr;\n"
                "};\n\n"
                "TEST_F(MXPrinterErrorTest, ErrorStringNotNull) {\n"
                "    for (int i = 0; i < 10; i++) {\n"
                "        const char* error_str = mx_get_error_string(static_cast<mx_error_t>(i));\n"
                "        EXPECT_NE(error_str, nullptr);\n"
                "        EXPECT_GT(strlen(error_str), 0);\n"
                "    }\n"
                "}\n\n"
                "TEST_F(MXPrinterErrorTest, InvalidHandleOperations) {\n"
                "    mx_device_info_t devices[1];\n"
                "    size_t device_count = 0;\n"
                "    mx_error_t result = mx_scan_devices(nullptr, devices, 1, &device_count);\n"
                "    EXPECT_NE(result, MX_SUCCESS);\n"
                "}\n"
            )
        endif()
    endif()
endforeach()

# 创建测试可执行文件
add_executable(mx_printer_tests
    ${TEST_SOURCES}
)

# 链接库
target_link_libraries(mx_printer_tests
    ${MXPrinter_LIBRARIES}
    GTest::gtest
    GTest::gtest_main
    GTest::gmock
)

# 设置目标属性
set_target_properties(mx_printer_tests PROPERTIES
    OUTPUT_NAME "mx_printer_tests"
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)

# 添加测试
add_test(
    NAME MXPrinterAllTests
    COMMAND mx_printer_tests
    WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
)

# 设置测试环境变量
set_tests_properties(MXPrinterAllTests PROPERTIES
    ENVIRONMENT "MX_PRINTER_TEST_MODE=1"
)

# 创建单独的测试目标
add_test(
    NAME MXPrinterBasicTests
    COMMAND mx_printer_tests --gtest_filter="MXPrinterBasicTest.*"
    WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
)

add_test(
    NAME MXPrinterDeviceTests
    COMMAND mx_printer_tests --gtest_filter="MXPrinterDeviceTest.*"
    WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
)

add_test(
    NAME MXPrinterImageTests
    COMMAND mx_printer_tests --gtest_filter="MXPrinterImageTest.*"
    WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
)

add_test(
    NAME MXPrinterErrorTests
    COMMAND mx_printer_tests --gtest_filter="MXPrinterErrorTest.*"
    WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
)

# 性能测试（可选）
option(BUILD_PERFORMANCE_TESTS "Build performance tests" OFF)

if(BUILD_PERFORMANCE_TESTS)
    # 查找 Google Benchmark
    find_package(benchmark QUIET)
    
    if(benchmark_FOUND)
        add_executable(mx_printer_benchmarks
            benchmark_mx_printer.cpp
        )
        
        target_link_libraries(mx_printer_benchmarks
            ${MXPrinter_LIBRARIES}
            benchmark::benchmark
        )
        
        # 创建基准测试文件
        if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/benchmark_mx_printer.cpp")
            file(WRITE "${CMAKE_CURRENT_SOURCE_DIR}/benchmark_mx_printer.cpp"
                "#include <benchmark/benchmark.h>\n"
                "#include \"mx_printer.h\"\n\n"
                "static void BM_MXPrinterInit(benchmark::State& state) {\n"
                "    for (auto _ : state) {\n"
                "        mx_handle_t handle = mx_init();\n"
                "        if (handle) {\n"
                "            mx_cleanup(handle);\n"
                "        }\n"
                "    }\n"
                "}\n"
                "BENCHMARK(BM_MXPrinterInit);\n\n"
                "BENCHMARK_MAIN();\n"
            )
        endif()
        
        message(STATUS "Performance tests enabled")
    else()
        message(WARNING "Google Benchmark not found, performance tests disabled")
    endif()
endif()

# 代码覆盖率（仅在 Debug 模式下）
if(CMAKE_BUILD_TYPE STREQUAL "Debug" AND CMAKE_COMPILER_IS_GNUCXX)
    option(ENABLE_COVERAGE "Enable code coverage" OFF)
    
    if(ENABLE_COVERAGE)
        target_compile_options(mx_printer_tests PRIVATE --coverage)
        target_link_libraries(mx_printer_tests PRIVATE --coverage)
        
        # 添加覆盖率报告目标
        find_program(GCOV_PATH gcov)
        find_program(LCOV_PATH lcov)
        find_program(GENHTML_PATH genhtml)
        
        if(GCOV_PATH AND LCOV_PATH AND GENHTML_PATH)
            add_custom_target(coverage
                COMMAND ${LCOV_PATH} --directory . --capture --output-file coverage.info
                COMMAND ${LCOV_PATH} --remove coverage.info '/usr/*' --output-file coverage.info
                COMMAND ${LCOV_PATH} --list coverage.info
                COMMAND ${GENHTML_PATH} -o coverage_report coverage.info
                WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
                COMMENT "Generating code coverage report"
            )
            
            message(STATUS "Code coverage enabled")
        else()
            message(WARNING "Coverage tools not found, coverage target disabled")
        endif()
    endif()
endif()

# 内存检查（Valgrind）
find_program(VALGRIND_PATH valgrind)
if(VALGRIND_PATH)
    add_custom_target(memcheck
        COMMAND ${VALGRIND_PATH} --tool=memcheck --leak-check=full --show-leak-kinds=all 
                --track-origins=yes --verbose --error-exitcode=1 
                $<TARGET_FILE:mx_printer_tests>
        DEPENDS mx_printer_tests
        WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
        COMMENT "Running memory check with Valgrind"
    )
    
    message(STATUS "Valgrind memory check target available")
endif()

# 静态分析（Clang Static Analyzer）
find_program(CLANG_ANALYZER scan-build)
if(CLANG_ANALYZER)
    add_custom_target(static_analysis
        COMMAND ${CLANG_ANALYZER} --status-bugs -o ${CMAKE_BINARY_DIR}/static_analysis_report 
                make mx_printer_tests
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Running static analysis with Clang Static Analyzer"
    )
    
    message(STATUS "Static analysis target available")
endif()

# 安装测试
install(TARGETS mx_printer_tests
    RUNTIME DESTINATION bin/tests
    COMPONENT Tests
)

# 安装测试脚本
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/run_tests.sh"
    "#!/bin/bash\n"
    "echo \"Running MX Printer SDK Tests\"\n"
    "echo \"========================\"\n\n"
    "# 运行所有测试\n"
    "./mx_printer_tests\n\n"
    "echo \"\nTest execution completed.\"\n"
)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/run_tests.sh"
    DESTINATION bin/tests
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
               GROUP_READ GROUP_EXECUTE
               WORLD_READ WORLD_EXECUTE
    COMPONENT Tests
)

# 打印构建信息
message(STATUS "")
message(STATUS "MX Printer SDK Tests Configuration:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "  Google Test: ${GTest_FOUND}")
message(STATUS "  Performance tests: ${BUILD_PERFORMANCE_TESTS}")
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    message(STATUS "  Code coverage: ${ENABLE_COVERAGE}")
endif()
message(STATUS "  Tests will be installed to: ${CMAKE_INSTALL_PREFIX}/bin/tests")
message(STATUS "")