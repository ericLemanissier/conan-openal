from conans import CMake, ConanFile, tools
import os


class OpenALConan(ConanFile):
    name = "openal"
    version = "1.19.0"
    md5 = "a98737cc8fe65eb9c91b82c719c6465f"
    description = "OpenAL Soft is a software implementation of the OpenAL 3D audio API."
    url = "http://github.com/bincrafters/conan-openal"
    homepage = "https://www.openal.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.1.5@conan/stable")

    def source(self):
        source_url = "https://github.com/kcat/openal-soft"
        tools.get("{0}/archive/openal-soft-{1}.tar.gz".format(source_url, self.version), self.md5)
        extracted_dir = "openal-soft-openal-soft-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        generator = None
        if self.settings.os == 'Windows' and self.settings.compiler == 'gcc':
            generator = 'MSYS Makefiles'
        cmake = CMake(self, generator=generator)
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.definitions['LIBTYPE'] = 'SHARED' if self.options.shared else 'STATIC'
        cmake.definitions['ALSOFT_UTILS'] = False
        cmake.definitions['ALSOFT_EXAMPLES'] = False
        cmake.definitions['ALSOFT_TESTS'] = False
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*COPYING", dst="licenses", keep_path=False, ignore_case=True)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["OpenAL32", 'winmm']
        else:
            self.cpp_info.libs = ["openal"]
        if self.settings.os == 'Linux':
            self.cpp_info.libs.extend(['dl', 'm'])
        elif self.settings.os == 'Macos':
            frameworks = ['AudioToolbox', 'CoreAudio']
            for framework in frameworks:
                self.cpp_info.exelinkflags.append("-framework %s" % framework)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        self.cpp_info.includedirs = ["include", "include/AL"]
        if not self.options.shared:
            self.cpp_info.defines.append('AL_LIBTYPE_STATIC')
