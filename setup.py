from setuptools import setup, find_packages

import versioneer


setup(
    name="ups-api",
    description="Validate street addresses with the UPS API",
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="https://github.com/mcflugen/ups",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=["click", "pandas", "requests"],
    setup_requires=[],
    packages=find_packages(),
    entry_points={"console_scripts": ["ups=ups.cli:ups"]},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
