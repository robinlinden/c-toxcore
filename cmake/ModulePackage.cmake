find_package(PkgConfig)

function(pkg_use_module mod pkg)
  if(PKG_CONFIG_FOUND)
    pkg_search_module(${mod} ${pkg})
  endif()
  if(${mod}_FOUND)
    link_directories(${${mod}_LIBRARY_DIRS})
    include_directories(${${mod}_INCLUDE_DIRS})
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${${mod}_CFLAGS_OTHER}" PARENT_SCOPE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${${mod}_CFLAGS_OTHER}" PARENT_SCOPE)

    foreach(dir ${${mod}_INCLUDE_DIRS})
      set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -isystem ${dir}" PARENT_SCOPE)
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -isystem ${dir}" PARENT_SCOPE)
    endforeach()
  endif()
endfunction()

function(install_module lib)
  if(BUILD_SHARED_LIBS)
    set_target_properties(${lib} PROPERTIES
      VERSION ${SOVERSION}
      SOVERSION ${SOVERSION_MAJOR}
    )
  endif()

  install(TARGETS ${lib}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  )

  string(REPLACE ";" " " ${lib}_PKGCONFIG_LIBS "${${lib}_PKGCONFIG_LIBS}")
  string(REPLACE ";" " " ${lib}_PKGCONFIG_REQUIRES "${${lib}_PKGCONFIG_REQUIRES}")

  configure_file(
    "${${lib}_SOURCE_DIR}/other/pkgconfig/${lib}.pc.in"
    "${CMAKE_BINARY_DIR}/${lib}.pc"
    @ONLY
  )

  configure_file(
    "${toxcore_SOURCE_DIR}/other/rpm/${lib}.spec.in"
    "${CMAKE_BINARY_DIR}/${lib}.spec"
    @ONLY
  )

  install(FILES
    ${CMAKE_BINARY_DIR}/${lib}.pc
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)

  foreach(sublib ${${lib}_API_HEADERS})
    string(REPLACE "^" ";" sublib ${sublib})
    list(GET sublib 0 header)

    install(FILES ${header} ${ARGN})
  endforeach()
endfunction()
