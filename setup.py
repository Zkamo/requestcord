from setuptools import setup, find_packages

setup(
    name="requestcord",
    version="1.0.0b0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "curl-cffi",
        "websocket-client",
        "colorama",
        "discord-protos"
    ],
    extras_require={
        "win": ["pywin32>=306; sys_platform == 'win32'"]
    },
    description="Advanced Discord API wrapper with modern features",
    author="Kamo",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    license_files=[],
)