from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

class _develop(develop):
    def run(self):
        develop.run(self)

setup(
    name='ThreeSidedCoin',
    version='0.1',
    description='A pybullet simulation to find optimal 3-sided coin geometry.',
    author = 'Tim Olson',
    author_email = 'timjolson@user.noreplay.github.com',
    packages = find_packages(),
    install_requires = ['numpy','pybullet','tqdm','matplotlib'],
    include_package_data=True,
    cmdclass={
        'develop': _develop,
        'install': _develop,
    }
)
