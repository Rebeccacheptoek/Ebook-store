from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in star_ebook_store/__init__.py
from star_ebook_store import __version__ as version

setup(
	name="star_ebook_store",
	version=version,
	description="Star Ebook Store",
	author="becky",
	author_email="rebeccacheptoek1@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
