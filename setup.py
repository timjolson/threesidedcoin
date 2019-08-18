from setuptools import setup

setup(
    name='ThreeSidedCoin',
    version='0.2',
    description='A pybullet simulation to find optimal 3-sided coin geometry.',
    author='Tim Olson',
    author_email='timjolson@user.noreplay.github.com',
    packages=[],
    install_requires=['numpy','pybullet','tqdm','matplotlib', 'scipy'],
)
