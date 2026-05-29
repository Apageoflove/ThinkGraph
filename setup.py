from setuptools import setup, find_packages

setup(
    name="thinkgraph",
    version="0.1.0",
    description="Reasoning trace analysis framework for thinking models",
    author="ThinkGraph",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "networkx>=3.0",
        "pyvis>=0.3.2",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "click>=8.1.0",
    ],
    extras_require={
        "demo": ["gradio>=4.0.0"],
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": ["thinkgraph=thinkgraph.cli:main"],
    },
)
