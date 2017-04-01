import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

if sys.version_info < (3,4):
    dependencies='arrow six pathlib'
else:
    dependencies='arrow six'

setup(
    name='inform',
    version='1.8.0',
    description='print & logging utilities for communicating with user',
    long_description=readme,
    author="Ken Kundert",
    author_email='inform@nurdletech.com',
    url='http://nurdletech.com/linux-utilities/inform',
    download_url='https://github.com/kenkundert/inform/tarball/master',
    license='GPLv3+',
    zip_safe=True,
    packages=['inform'],
    install_requires=dependencies.split(),
    setup_requires='pytest-runner>=2.0'.split(),
    tests_require='pytest'.split(),
    keywords='inform logging printing'.split(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)
