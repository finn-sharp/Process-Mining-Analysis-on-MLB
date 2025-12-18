from setuptools import setup, find_packages
from pathlib import Path

def parse_requirements(path: str) -> list[str]:
    reqs = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r", "--")):
            continue
        reqs.append(line)
    return reqs

setup(
    name="my-project-pkg",
    version="0.1.0",
    python_requires=">=3.10",
    packages=find_packages(include=["mining*", "clustering*", "metrics*"]),
    install_requires=parse_requirements("requirements.txt"),
)
