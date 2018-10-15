from setuptools import setup, find_packages

setup(
    name='ThreeSidedCoin',
    version='0.1',
    description='A pybullet simulation to find optimal 3-sided coin geometry.',
    author = 'Tim Olson',
    author_email = 'timjolson@user.noreplay.github.com',
    packages = find_packages(),
    install_requires = ['numpy','pybullet','tqdm','matplotlib', 'scipy'],
    include_package_data=True,
)
