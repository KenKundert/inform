try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='inform',
    version='1.6.0',
    description='print & logging utilities for communicating with user',
    long_description=readme,
    author="Ken Kundert",
    author_email='inform@nurdletech.com',
    url='http://nurdletech.com/linux-utilities/inform',
    download_url='https://github.com/kenkundert/inform/tarball/master',
    license='GPLv3+',
    zip_safe=True,
    packages=['inform'],
    install_requires=[
        'arrow',
        'six',
    ],
    keywords=[
        'inform',
        'logging',
        'printing',
    ],
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
