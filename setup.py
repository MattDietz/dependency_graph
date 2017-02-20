import sys
import distutils.core

try:
    import setuptools
except ImportError:
    pass

version = "0.01"


distutils.core.setup(
    name="dependency_graph",
    version=version,
    packages = ["dependency_graph",],
    package_data = {
        "dependency_graph": [],
        },
    author="Matthew Dietz",
    author_email="matthew.dietz@gmail.com",
    url="",
    download_url="",
    license="https://opensource.org/licenses/MIT",
    description="",
    entry_points={}
    )
