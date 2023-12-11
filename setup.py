from setuptools import setup, find_packages

requires = [
    "inmanta-core>=6.0.0.dev",
    "tornado~=6.0",
]

namespace_packages = ["inmanta_ext.ui"]

setup(
    version="4.1.0",
    python_requires=">=3.9",  # also update classifiers
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
