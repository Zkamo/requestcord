from setuptools import setup, find_packages

def readme():
    with open("README.rst") as f:
        README = f.read()
    return README
setup(
    name="requestcord",
    version="2.0.1",
    packages=find_packages(),
    install_requires=[
        "curl-cffi",
        "websocket-client",
        "discord-protos"
    ],
    extras_require={
        "win": ["pywin32>=306; sys_platform == 'win32'"]
    },
    keywords=["discord", "api", "wrapper", "requestcord"],
    description="Advanced Discord API wrapper with modern features",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Zkamo & VatosV2",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">3.10"
)