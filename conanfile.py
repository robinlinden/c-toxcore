# pylint: disable=not-callable
import os
import re

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import collect_libs
from conan.tools.files import load


class ToxConan(ConanFile):
    name = "c-toxcore"
    url = "https://tox.chat"
    description = "The future of online communications."
    license = "GPL-3.0-only"
    settings = "os", "compiler", "build_type", "arch"
    requires = "libsodium/1.0.18", "opus/1.3.1", "libvpx/1.9.0"
    generators = "CMakeDeps"
    scm = {"type": "git", "url": "auto", "revision": "auto"}

    options = {
        "shared": [True, False],
        "with_tests": [True, False],
    }
    default_options = {
        "shared": False,
        "with_tests": False,
    }

    def generate(self):
        cmake = CMakeToolchain(self)
        cmake.cache_variables = {
            "AUTOTEST": self.options.with_tests,
            "BUILD_MISC_TESTS": self.options.with_tests,
            "TEST_TIMEOUT_SECONDS": "300",

            "CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS": self.options.shared,
            "ENABLE_SHARED": self.options.shared,
            "ENABLE_STATIC": not self.options.shared,
            "MUST_BUILD_TOXAV": True,
        }

        if self.settings.compiler == "msvc":
            cmake.cache_variables["MSVC_STATIC_SODIUM"] = True
            cmake.cache_variables["FLAT_OUTPUT_STRUCTURE"] = self.options.shared

        cmake.generate()

    def set_version(self):
        content = load(self, os.path.join(self.recipe_folder, "CMakeLists.txt"))
        version_major = re.search(r"set\(PROJECT_VERSION_MAJOR \"(.*)\"\)",
                                  content).group(1)
        version_minor = re.search(r"set\(PROJECT_VERSION_MINOR \"(.*)\"\)",
                                  content).group(1)
        version_patch = re.search(r"set\(PROJECT_VERSION_PATCH \"(.*)\"\)",
                                  content).group(1)
        self.version = "%s.%s.%s" % (
            version_major.strip(),
            version_minor.strip(),
            version_patch.strip(),
        )

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("pthreads4w/3.0.0")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if self.options.with_tests:
            cmake.test(output_on_failure=True)

    def package(self):
        cmake = self._create_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Ws2_32", "Iphlpapi"]
