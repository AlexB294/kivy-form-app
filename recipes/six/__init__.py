from pythonforandroid.recipe import PythonRecipe

class SixRecipe(PythonRecipe):
    version = "1.16.0"
    url = "https://pypi.python.org/packages/source/s/six/six-{version}.tar.gz"

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        # make sure setuptools & wheel are available in hostpython
        hostpython = self.ctx.hostpython
        self.ctx.cmd(hostpython, "-m", "pip", "install", "--upgrade", "setuptools", "wheel")

recipe = SixRecipe()
