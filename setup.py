"""
安装配置
"""

from setuptools import setup, find_packages
import config

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name=config.APP_NAME.lower().replace(" ", "-"),
    version=config.APP_VERSION,
    author=config.APP_AUTHOR,
    author_email="your.email@example.com",
    description="基于AI的智能视频解说工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aicraft-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aicraft=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.qss", "*.png", "*.jpg", "*.ico"],
    },
)
