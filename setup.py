from setuptools import setup

setup(
    name='DVD2LS',
    version='0.1.0',
    packages=['dvd2ls'],
    url='',
    license='',
    author='AMIA Open Source',
    author_email='',
    description='',
    test_suite="tests",
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    install_requires=['isoparser', 'six'],
    entry_points={
        'console_scripts': [
            "dvd2ls = dvd2ls.dvd_transcoder:main"
        ]
    }
)
