from setuptools import setup, find_packages

def readme():
    with open("README.md") as f:
        README = f.read()
    return README
setup(
    name="requestcord",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "curl-cffi",
        "websocket-client",
        "websockets",
        "colorama",
        "discord-protos",
        "aiohttp",
        "asyncio"
    ],
    extras_require={
        "win": ["pywin32>=306; sys_platform == 'win32'"]
    },
    description="Advanced Discord API wrapper with modern features",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Kamo",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8"
)
