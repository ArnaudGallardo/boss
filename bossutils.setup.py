import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bossutils",
    version="1.0.6",
    author="JHU/APL",
    author_email="BossAdmin@jhuapl.edu",
    description="General Boss Python3 library used by many of the VMs running Boss code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhuapl-boss/boss-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)