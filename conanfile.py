#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class LibX264Conan(ConanFile):
    name = "libx264"
    version = "20171211"
    url = "https://github.com/bincrafters/conan-libx264"
    homepage = "https://www.videolan.org/developers/x264.html"
    description = "x264 is a free software library and application for encoding video streams into the " \
                  "H.264/MPEG-4 AVC compression format"
    license = "http://git.videolan.org/?p=x264.git;a=blob;f=COPYING"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "bit_depth": [8, 10]}
    default_options = {'shared': False, 'fPIC': True, 'bit_depth': '8'}
    build_requires = "nasm_installer/2.13.02@bincrafters/stable"
    _source_subfolder = "sources"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc' and os.name == 'nt'

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def build_requirements(self):
        if self._is_mingw_windows or self._is_msvc:
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        source_url =\
            "http://download.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-%s-2245.tar.bz2" % self.version
        tools.get(source_url)
        extracted_dir = 'x264-snapshot-%s-2245' % self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            args = ['--disable-cli']
            if self.options.shared:
                args.append('--enable-shared')
            else:
                args.append('--enable-static')
            if self.settings.os != 'Windows' and self.options.fPIC:
                args.append('--enable-pic')
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            args.append('--bit-depth=%s' % str(self.options.bit_depth))

            env_vars = dict()
            if self._is_msvc:
                env_vars['CC'] = 'cl'
            with tools.environment_append(env_vars):
                env_build = AutoToolsBuildEnvironment(self, win_bash=self._is_mingw_windows or self._is_msvc)
                if self._is_msvc:
                    env_build.flags.append('-%s' % str(self.settings.compiler.runtime))
                    # cannot open program database ... if multiple CL.EXE write to the same .PDB file, please use /FS
                    env_build.flags.append('-FS')
                env_build.configure(args=args, build=False, host=False)
                env_build.make()
                env_build.install()

    def build(self):
        if self._is_msvc:
            with tools.vcvars(self.settings):
                self._build_configure()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="COPYING", src='sources', dst='licenses')

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ['libx264.dll.lib' if self.options.shared else 'libx264']
        elif self._is_mingw_windows:
            self.cpp_info.libs = ['x264.dll' if self.options.shared else 'x264']
        else:
            self.cpp_info.libs = ['x264']
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(['dl', 'pthread'])
