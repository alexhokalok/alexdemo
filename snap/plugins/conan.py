# MIT License

# Copyright (c) [year] [fullname]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The conan plugin is used for projects that rely on conan.io as their package manager
Conan based projects usually have the following instruction set
`conan install . && conan build`
This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.
In addition, this plugin uses the following plugin-specific keywords:
	- missing
		(boolean)
		will install dependencies with the `install --build=missing` flag
		which issues build by source for any dependency
"""

import os
import stat
import shutil
import logging

import snapcraft

#from snapcraft.plugins import PythonPlugin # the python plugin could be extended, but this is much easier..

logger = logging.getLogger(__name__)

import json
class ConanPlugin(snapcraft.BasePlugin):
	@classmethod
	def schema(self):
		schema = super().schema()
		schema['properties']['missing'] = {
			'type': 'boolean',
			'default': 'false',
		}
		schema["properties"]["configflags"] = {
            		"type": "array",
			"minitems": 1,
			"uniqueItems": True,
			"items": {"type": "string"},
			"default": [],
		}

		return schema

	@property
	def plugin_build_packages(self):
		return [
			"python-dev",
			"python-pip",
			"python-pkg-resources",
			"python-setuptools",
		]

	def __init__(self, name, options, project):
		super().__init__(name, options, project)
		self.build_packages.extend(self.plugin_build_packages)

		if options.missing:
			self.install_missing = True
		else:
			self.install_missing = False

	def pull(self):
		super().pull()


	def _update_conan_profile(self):
		conan_profile_path = os.path.join(os.path.expanduser("~"), ".conan", "profiles", self._target)
		new_profile_command = ["conan", "profile", "new", self._target, "--detect"]
		print(conan_profile_path)
		if not os.path.exists(conan_profile_path):
			self.run(new_profile_command)
		update_profile_command = ["conan", "profile", "update"]
		update_compiler = update_profile_command + ["settings.compiler=gcc", self._target]
#		update_compiler_version = update_profile_command + ["settings.compiler.version=7", self._target]
		update_arch = update_profile_command + ["settings.arch={}".format(self._target), self._target]
		update_CFLAG = update_profile_command + ["env.CFLAG=\"-arch {}\"".format(self._target), self._target]
		update_CXXFLAG = update_profile_command + ["env.CXXFLAG=\"-arch {}\"".format(self._target), self._target]
		self.run(update_compiler)
#		self.run(update_compiler_version)
		self.run(update_arch)
		self.run(update_CFLAG)
		self.run(update_CXXFLAG)


	def enable_cross_compilation(self):
		if not self.project.is_cross_compiling:
			return
		logger.info("Cross compiling to {!r}".format(self.project.kernel_arch))
		targets = {
			"armhf": "armv7hf",
			"arm": "armv7",
			"arm64": "armv8",
			"x86": "x86",
			"amd64": "x86_64"
		}
		self._target = targets.get(self.project.kernel_arch)
		if not self._target:
			raise NotImplementedError(
		                "{!r} is not supported as a target architecture when "
		                "cross-compiling with the conan plugin".format(self.project.deb_arch)
			)

	def _build_env(self):
		env = os.environ.copy()
		if self.project.is_cross_compiling:
			env.update({
				"CFLAG": "{} -arch {}".format(env.get("CFLAG"), self._target),
				"CXXFLAG": "{} -arch {}".format(env.get("CFLAG"), self._target)
			})
		return env

	def build(self):
		super().build()

		os.chdir(self.builddir)
		print("build:",self.builddir)
		libdir = os.path.abspath(os.path.join(self.builddir, 'lib'))
		bindir = os.path.abspath(os.path.join(self.builddir, 'bin'))
		install_command = ['conan', 'install', os.path.abspath(os.path.join(self.builddir, os.pardir, 'src'))]
		build_command = ['conan', 'build', os.path.abspath(os.path.join(self.builddir, os.pardir, 'src'))]

		if self.install_missing:
			# Build missing dependencies
			install_command.append('--build=missing')

		if self.project.is_cross_compiling:
			self._update_conan_profile()
			install_command.append("--profile")
			install_command.append(self._target)
#			update_profile_arch_command = update_profile_command + ['settings.arch={}'.format(self._target)]

		self.run(install_command, env=self._build_env())
		self.run(build_command) # Unfortanly I couldn't find any -j flag for the build commands
		for dir in ['bin', 'lib']:
			build_path = os.path.join(self.builddir, dir)
			if os.path.exists(build_path):
				install_path = os.path.join(self.installdir, dir)
				shutil.copytree(build_path, install_path)


	def snap_fileset(self):
		fileset = super().snap_fileset()
		return fileset
		# Since snap stores all dependencies occasionally in ~./conan we don't need no file stripping

