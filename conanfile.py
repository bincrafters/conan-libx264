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
    options = {"shared": [True, False], "fPIC": [True, False], "bit_depth": [8, 10]}
    default_options = "shared=False", "fPIC=True", "bit_depth=8"

    @property
    def is_mingw(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc'

    @property
    def is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def build_requirements(self):
        self.build_requires("nasm_installer/[>=2.13.02]@bincrafters/stable")

    def configure(self):
        del self.settings.compiler.libcxx
        if self.is_msvc:
            del self.options.fPIC

    def source(self):
        source_url =\
            "http://download.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-%s-2245.tar.bz2" % self.version
        tools.get(source_url)
        extracted_dir = 'x264-snapshot-%s-2245' % self.version
        os.rename(extracted_dir, "sources")

    def build_configure(self):
        with tools.chdir('sources'):
            prefix = os.path.abspath(self.package_folder)
            win_bash = False
            if self.is_mingw or self.is_msvc:
                win_bash = True
                prefix = tools.unix_path(prefix, tools.CYGWIN)
            args = ['--prefix=%s' % prefix]
            if self.options.shared:
                args.append('--enable-shared')
            else:
                args.append('--enable-static')
            if not self.is_msvc and self.options.fPIC:
                args.append('--enable-pic')
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            args.append('--bit-depth=%s' % str(self.options.bit_depth))

            env_vars = dict()
            if self.is_msvc:
                env_vars['CC'] = 'cl'
            with tools.environment_append(env_vars):
                env_build = AutoToolsBuildEnvironment(self, win_bash=win_bash)
                if self.is_msvc:
                    env_build.flags.append('-%s' % str(self.settings.compiler.runtime))
                env_build.configure(args=args)
                env_build.make()
                env_build.make(args=['install'])

    def build(self):
        if self.settings.os == 'Windows':
            cygwin_bin = self.deps_env_info['cygwin_installer'].CYGWIN_BIN
            with tools.environment_append({'PATH': [cygwin_bin],
                                           'CONAN_BASH_PATH': '%s/bash.exe' % cygwin_bin}):
                if self.is_msvc:
                    with tools.vcvars(self.settings):
                        self.build_configure()
                elif self.is_mingw:
                    self.build_configure()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="COPYING", src='sources')

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs = ['libx264.dll.lib' if self.options.shared else 'libx264']
        elif self.is_mingw:
            self.cpp_info.libs = ['x264.dll' if self.options.shared else 'x264']
        else:
            self.cpp_info.libs = ['x264']
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(['dl', 'pthread'])
