try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='messenger',
    version='1.0.5',
    description='Quicksilver Messenger Service',
    long_description=readme,
    author="Ken Kundert",
    author_email='messenger@nurdletech.com',
    url='https://github.com/kenkundert/messenger',
    license='GPLv3+',
    zip_safe=True,
    packages=['messenger'],
    install_requires=[
        'arrow',
        'six',
    ],
    keywords=[
        'messenger',
        'quicksilver',
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
        'Topic :: Utilities',
    ],
)
