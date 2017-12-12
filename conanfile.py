#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class LibX264Conan(ConanFile):
    name = "libx264"
    version = "20171211"
    url = "https://github.com/bincrafters/conan-libx264"
    description = "x264 is a free software library and application for encoding video streams into the " \
                  "H.264/MPEG-4 AVC compression format"
    license = "http://git.videolan.org/?p=x264.git;a=blob;f=COPYING"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        source_url =\
            "http://download.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-%s-2245.tar.bz2" % self.version
        tools.get(source_url)
        extracted_dir = 'x264-snapshot-%s-2245' % self.version
        os.rename(extracted_dir, "sources")

    def build_vs(self):
        raise Exception("TODO")

    def build_configure(self):
        with tools.chdir('sources'):
            args = ['--prefix=%s' % self.package_folder]
            args.append('--disable-asm') # TEMP!!!
            if self.options.shared:
                args.append('--enable-shared')
            else:
                args.append('--enable-static')
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="COPYING", src='sources')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
