from setuptools import setup, find_packages

setup(
    name="mlb_process", 
    version="0.1.0",
    description="Process mining / clustering / metrics toolkit",
    python_requires=">=3.13",
    packages=find_packages(include=["mining*", "clustering*", "metrics*"]),
    include_package_data=True,
)
