from conans import ConanFile, CMake, tools
import os


class OpenscenegraphConan(ConanFile):
    name = "openscenegraph"
    version = "3.6.5"
    description = "OpenSceneGraph is an open source high performance 3D graphics toolkit"
    topics = ("conan", "openscenegraph", "graphics")
    url = "https://github.com/bincrafters/conan-openscenegraph"
    homepage = "https://github.com/openscenegraph/OpenSceneGraph"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    short_paths = True
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_osg_applications": [True, False],
        "build_osg_plugins_by_default": [True, False],
        "build_osg_examples": [True, False],
        "dynamic_openthreads": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_osg_applications": False,
        "build_osg_plugins_by_default": False,
        "build_osg_examples": False,
        "dynamic_openthreads": True
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "zlib/1.2.11",
        "freetype/2.10.4",
        "libjpeg/9d",
        "libxml2/2.9.10",
        "libcurl/7.67.0",
        "libpng/1.6.37",
        "libtiff/4.0.9",
        "sdl2/2.0.12@bincrafters/stable",
        "jasper/2.0.19",
        "cairo/1.17.2",
        # "openblas/0.3.12", Removed until openblas is in conan center
    )

    _cmake = None

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("asio/1.13.0")
        if self.settings.os == "Linux":
            self.requires("xorg/system")
        self.requires("opengl/system")
        self.requires("glu/system")

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                installer.install("libegl1-mesa-dev")
                installer.install("libgtk2.0-dev")
                installer.install("libpoppler-glib-dev")
            else:
                self.output.warn("Could not determine Linux package manager, skipping system requirements installation.")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        prefix = "OpenSceneGraph"
        sha256 = "aea196550f02974d6d09291c5d83b51ca6a03b3767e234a8c0e21322927d1e12"
        tools.get("{0}/archive/{1}-{2}.tar.gz".format(self.homepage, prefix, self.version), sha256=sha256)
        extracted_dir = "{}-{}-".format(prefix, prefix) + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_OSG_APPLICATIONS"] = self.options.build_osg_applications
            self._cmake.definitions["DYNAMIC_OPENSCENEGRAPH"] = self.options.shared
            self._cmake.definitions["BUILD_OSG_PLUGINS_BY_DEFAULT"] = self.options.build_osg_plugins_by_default
            self._cmake.definitions['BUILD_OSG_EXAMPLES'] = self.options.build_osg_examples
            self._cmake.definitions["DYNAMIC_OPENTHREADS"] = self.options.dynamic_openthreads

            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions['BUILD_WITH_STATIC_CRT'] = "MT" in str(self.settings.compiler.runtime)

            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("rt")
        if not self.options.shared:
            self.cpp_info.defines.append("OSG_LIBRARY_STATIC=1")
