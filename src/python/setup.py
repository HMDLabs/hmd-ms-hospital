from setuptools import setup, find_packages
import pathlib

repo_dir = pathlib.Path(__file__).absolute().parent.parent.parent
version_file = repo_dir / "meta-data" / "VERSION"

with open(version_file, "r") as vfl:
    version = vfl.read().strip()

setup(
    name="hmd-ms-hospital",
    version=version,
    description="Hospital Microservice",
    author="Alex Burgoon",
    author_email="alex.burgoon@hmdlabs.io",
    license="unlicensed",
    package_data={"hmd_lang_hospital": ["schemas/**/*.hms"]},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
)
