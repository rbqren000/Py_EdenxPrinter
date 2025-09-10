# MXPrinterConfig.cmake.in
# MX Printer SDK CMake配置文件
# 作者: RBQ



include(CMakeFindDependencyMacro)

# 检查组件
set(_MXPrinter_supported_components static shared)

foreach(_comp ${MXPrinter_FIND_COMPONENTS})
    if (NOT _comp IN_LIST _MXPrinter_supported_components)
        set(MXPrinter_FOUND False)
        set(MXPrinter_NOT_FOUND_MESSAGE "Unsupported component: ${_comp}")
    endif()
endforeach()

# 包含目标文件
include("${CMAKE_CURRENT_LIST_DIR}/MXPrinterTargets.cmake")

# 设置变量
set(MXPrinter_VERSION 1.0.0)
set(MXPrinter_INCLUDE_DIRS "${PACKAGE_PREFIX_DIR}/include")

# 根据请求的组件设置库
if("static" IN_LIST MXPrinter_FIND_COMPONENTS)
    set(MXPrinter_LIBRARIES MXPrinter::mx_printer_static)
elseif("shared" IN_LIST MXPrinter_FIND_COMPONENTS)
    set(MXPrinter_LIBRARIES MXPrinter::mx_printer_shared)
else()
    # 默认使用静态库
    set(MXPrinter_LIBRARIES MXPrinter::mx_printer_static)
endif()

check_required_components(MXPrinter)
