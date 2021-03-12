from setuptools import setup, find_packages

requires = [
    "inmanta==2020.4.5",
    "tornado",
]

namespace_packages = ["inmanta_ext.ui"]

setup(
    version="1.2.4",
    python_requires=">=3.6",  # also update classifiers
    # Meta data
    name="inmanta-ui",
    description="Slice serving the inmanta UI",
    author="Inmanta",
    author_email="code@inmanta.com",
    url="https://github.com/inmanta/inmanta-ui",
    license="ASL 2.0",
    project_urls={
        "Bug Tracker": "https://github.com/inmanta/inmanta-ui/issues",
    },
    # Packaging
    package_dir={"": "src"},
    packages= namespace_packages + find_packages("src"),
    package_data={"": ["misc/*", "docs/*"]},
    include_package_data=True,
    install_requires=requires,
    entry_points={
    },
)
