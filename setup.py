from distutils.core import setup, find_packages


setup(
    name='repeatedmistakes',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'nose >= 1.3.7',
        'hypothesis >= 1.10.1',
        'numpy >= 1.9.2',
        'pandas >= 0.16.2'
    ],
    url='https://github.com/computationalevolutionarydynamics/repeatedmistakes',
    license='GNU GPL v3 (see LICENSE)',
    author='Nikolas Skoufis',
    author_email='n.skoufis@gmail.com',
    description="""
                A package for studying the iterated prisoners dilemma with mistakes
                """
)
