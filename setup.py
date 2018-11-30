from setuptools import setup

setup(
    name='dvd2dv25',
    version='0.1.0',
    packages=['dvd2dv25'],
    url='',
    license='',
    author='AMIA Open Source',
    author_email='',
    description='',
    test_suite="tests",
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    install_requires=['isoparser'],
    entry_points={
        'console_scripts': [
            "dvd2dv25 = dvd2dv25.dvd_transcoder:main"
        ]
    }
)
