from setuptools import setup, find_packages

setup(
    name="skilly",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "skilly=skilly_core.cli:main",
        ],
    },
    install_requires=[
        "networkx>=2.8",
        "rich>=12.0.0",
    ],
    python_requires=">=3.8",
)
