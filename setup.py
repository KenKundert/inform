import sys
from setuptools import setup
from codecs import open

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

if sys.version_info < (3,4):
    dependencies='arrow six pathlib'
else:
    dependencies='arrow six'

setup(
    name = 'inform',
    version = '1.25.0',
    description = 'print & logging utilities for communicating with user',
    long_description = readme,
    long_description_content_type = 'text/x-rst',
    author = "Ken Kundert",
    author_email = 'inform@nurdletech.com',
    url = 'https://inform.readthedocs.io',
    download_url = 'https://github.com/kenkundert/inform/tarball/master',
    license = 'GPLv3+',
    zip_safe = False,
    packages = ['inform'],
    install_requires = dependencies.split(),
    setup_requires = 'pytest-runner>=2.0'.split(),
    tests_require = 'pytest pytest-cov hypothesis'.split(),
    python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
    keywords = 'inform logging printing'.split(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
    ],
)
