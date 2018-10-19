from conans import ConanFile, CMake, tools


class FilemetaConan(ConanFile):
    name = "file-meta"
    version = "0.1.0"
    license = "MIT"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "A demo package which compute file meta"
    requires = (("gflags/2.2.1@bincrafters/stable"),
                ("OpenSSL/1.1.0i@conan/stable"),
                ("boost/1.68.0@conan/stable"))
    build_policy = "missing"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=True", "fPIC=True"
    generators = "cmake"

    exports_sources = "file-meta/*"

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="file-meta")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="file-meta/include")
#        if self.options.shared:
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
#        else:
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hashes"]
