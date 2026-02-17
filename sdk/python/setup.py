from setuptools import setup, find_packages

setup(
    name="realchat-sdk",
    version="1.0.0",
    description="Connect any LLM/agent to WeChat through the RealChat universal bridge",
    packages=find_packages(),
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
