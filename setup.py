# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='cli',
    version='0.0.1',
    author='François Ménabé',
    author_email='francois.menabe@gmail.com',
    #url='',
    #download_url='',
    license='MIT License',
    description='Framework for generating command-line',
    long_description=open('README.rst').read(),
    keywords=['command-line', 'argparse', 'wrapper', 'clg', 'framework'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    packages=['cli'])
