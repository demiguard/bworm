from setuptools import setup, find_packages

setup(
  version="0.0.1",
  name="bworm",
  description="The best worst ORM (Object Relation Mapping) out there!",
  author="Demiguard",
  package_dir={"" : "src"},
  packages=find_packages(where="src")
)
