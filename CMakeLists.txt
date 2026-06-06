cmake_minimum_required(VERSION 3.16)

#------------------------------------------------------------------
# Extension Meta-information
#------------------------------------------------------------------
set(EXTENSION_NAME SlicerAIAgent)
set(EXTENSION_CATEGORY "AI")
set(EXTENSION_CONTRIBUTORS "Puxun (Agent Developer)")
set(EXTENSION_DESCRIPTION "An AI-powered assistant extension for 3D Slicer using KIMI API. Provides intelligent code generation, scene manipulation through natural language, and guided workflows.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/yourusername/SlicerAIAgent/main/SlicerAIAgent.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/yourusername/SlicerAIAgent/main/screenshots/screenshot1.png")
set(EXTENSION_DEPENDS "NA")
set(EXTENSION_LICENSE_FILE ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE)
set(EXTENSION_README_FILE ${CMAKE_CURRENT_SOURCE_DIR}/README.md)
set(EXTENSION_BUILD_SUBDIRECTORY ${EXTENSION_NAME}-build)

#------------------------------------------------------------------
# Find Slicer
#------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#------------------------------------------------------------------
# Install Python dependencies
#------------------------------------------------------------------
set(requirements_file ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt)
if(EXISTS ${requirements_file})
  file(STRINGS ${requirements_file} requirements)
  foreach(requirement ${requirements})
    string(STRIP ${requirement} requirement)
    if(requirement AND NOT requirement MATCHES "^#")
      slicer_install_python_package(
        PACKAGE_NAME ${requirement}
        PACKAGE_MANAGER "pip"
      )
    endif()
  endforeach()
endif()

#------------------------------------------------------------------
# Extension Modules
#------------------------------------------------------------------
# Scripted modules
set(modules
  SlicerAIAgent
  )

file(GLOB_RECURSE SLICER_AI_AGENT_LIBRARY_PYTHON_FILES
  CONFIGURE_DEPENDS
  ${CMAKE_CURRENT_SOURCE_DIR}/SlicerAIAgentLib/*.py
  )

foreach(module ${modules})
  slicerMacroBuildScriptedModule(
    NAME ${module}
    SCRIPTS ${module}.py ${SLICER_AI_AGENT_LIBRARY_PYTHON_FILES}
    RESOURCES Resources
    )
endforeach()

#------------------------------------------------------------------
# Testing
#------------------------------------------------------------------
if(BUILD_TESTING)
  file(GLOB_RECURSE SLICER_AI_AGENT_TEST_PYTHON_FILES
    CONFIGURE_DEPENDS
    ${CMAKE_CURRENT_SOURCE_DIR}/Testing/*.py
    )
  slicerMacroBuildScriptedModule(
    NAME SlicerAIAgentTest
    SCRIPTS ${SLICER_AI_AGENT_TEST_PYTHON_FILES}
    )
endif()

#------------------------------------------------------------------
# Packaging
#------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
