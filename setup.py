from setuptools import setup, find_packages

setup(
    name="skilly-ai",
    version="1.0.1",
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
