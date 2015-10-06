from setuptools import setup, find_packages

setup(
    name='repeatedmistakes',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'nose',
        'hypothesis',
        'numpy',
        'scipy',
    ],
    url='https://github.com/computationalevolutionarydynamics/repeatedmistakes',
    license='GNU GPL v3 (see LICENSE)',
    author='Nikolas Skoufis',
    author_email='n.skoufis@gmail.com',
    description="""
                A package for studying the iterated prisoners dilemma with mistakes
                """
)
