#!/usr/bin/env python
# coding: utf-8
import os
import textwrap

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version


class AbseilConan(ConanFile):
    name = "abseil"
    version = "20190808"
    url = "https://github.com/abseil/abseil-cpp"
    homepage = url
    author = "Abseil <abseil-io@googlegroups.com>"
    description = "Abseil Common Libraries (C++) from Google"
    license = "Apache-2.0"
    topics = ("conan", "abseil", "abseil-cpp", "google", "common-libraries")
    exports = ["LICENSE"]
    exports_sources = ["*.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    _sha256 = "8100085dada279bf3ee00cd064d43b5f55e5d913be0dfe2906f06f8f28d5b37e"
    _source_dir = "abseil-cpp-{0}".format(version)

    def source(self):
        tools.get(
            "{0}/archive/{1}.tar.gz".format(self.homepage, self.version),
            keep_permissions=True,
            sha256=self._sha256,
        )
        tools.replace_in_file(
            os.path.join(self._source_dir, "CMakeLists.txt"),
            "project(absl CXX)",
            textwrap.dedent(
                """\
                project(absl CXX)
                if (POLICY CMP0063)
                  # Honour CMake visibility props
                  cmake_policy(SET CMP0063 NEW)
                endif ()
                include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
                conan_basic_setup()
                """
            ).rstrip(),
        )
        tools.patch(
            patch_file="0001-Add-work-around-to-fix-MSVC-debug-build-errors.patch",
            base_path=self._source_dir,
        )

    def configure(self):
        if (
            self.settings.os == "Windows"
            and self.settings.compiler == "Visual Studio"
            and Version(self.settings.compiler.version.value) < "14"
        ):
            raise ConanInvalidConfiguration("Abseil does not support MSVC < 14")

        cppstd = str(self.settings.compiler.cppstd or "")
        if (
            self.settings.compiler != "Visual Studio"
            and cppstd
            and not cppstd.startswith("gnu")
        ):
            self.settings.compiler.cppstd = "gnu{}".format(cppstd)

    def _configure_cmake(self):
        cmake = CMake(self, generator="Ninja")
        cmake.verbose = True
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True
        cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = True

        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure(source_folder=self._source_dir)
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_dir)
        self.copy("*.h", dst="include", src=self._source_dir)
        self.copy("*.inc", dst="include", src=self._source_dir)
        self.copy("*.a", dst="lib", src=".", keep_path=False)
        self.copy("*.lib", dst="lib", src=".", keep_path=False)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["-Wl,--start-group"]
        self.cpp_info.libs.extend(tools.collect_libs(self))
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["-Wl,--end-group", "pthread"])

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags = [
                "-framework CoreFoundation"
            ]
