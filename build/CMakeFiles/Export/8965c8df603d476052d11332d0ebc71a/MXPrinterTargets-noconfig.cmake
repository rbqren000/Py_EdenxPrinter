#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "MXPrinter::mx_printer_static" for configuration ""
set_property(TARGET MXPrinter::mx_printer_static APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(MXPrinter::mx_printer_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_NOCONFIG "C"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/macos/arm64/libmx_printer.a"
  )

list(APPEND _cmake_import_check_targets MXPrinter::mx_printer_static )
list(APPEND _cmake_import_check_files_for_MXPrinter::mx_printer_static "${_IMPORT_PREFIX}/lib/macos/arm64/libmx_printer.a" )

# Import target "MXPrinter::mx_printer_shared" for configuration ""
set_property(TARGET MXPrinter::mx_printer_shared APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(MXPrinter::mx_printer_shared PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/macos/arm64/libmx_printer.dylib"
  IMPORTED_SONAME_NOCONFIG "@rpath/libmx_printer.dylib"
  )

list(APPEND _cmake_import_check_targets MXPrinter::mx_printer_shared )
list(APPEND _cmake_import_check_files_for_MXPrinter::mx_printer_shared "${_IMPORT_PREFIX}/lib/macos/arm64/libmx_printer.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
