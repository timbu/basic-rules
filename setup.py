from setuptools import setup, find_packages

setup(
    name='basicrules',
    version='0.0.1',
    description='Basic rule functions',
    author='timbu',
    url='http://github.com/timbu/basic-rules',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[],
    extras_require={
        'dev': [
            "coverage==4.5.2",
            "flake8==3.7.4",
            "pylint==2.2.2",
            "pytest==4.2.0",
        ]
    },
    zip_safe=True,
    license='Apache License, Version 2.0',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
