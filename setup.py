from setuptools import setup, find_packages

setup(
    name="groqee2",
    version="1.0.0",
    description="Groqee Web Assistant",
    author="John Daniel Dondlinger",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",  # Add other dependencies here
    ],
    entry_points={
        "console_scripts": [
            "groqee2=app:main",  # Replace `app:main` with your entry point
        ],
    },
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
)