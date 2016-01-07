try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='messenger',
    version='1.0.0',
    description='Quicksilver Messenger Service',
    long_description=readme,
    author="Ken Kundert",
    author_email='messenger@nurdletech.com',
    url='https://github.com/kenkundert/messenger',
    license='GPLv3+',
    zip_safe=True,
    keywords=[
        'messenger',
        'quicksilver',
    ],
    py_modules=['messenger'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
