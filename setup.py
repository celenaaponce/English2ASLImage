import setuptools

setuptools.setup(
    name="streamlit-streamlit-selected-text-display",
    version="0.0.1",
    author="John Smith",
    author_email="john@example.com",
    description="Streamlit component that allows you to do X",
    long_description=""
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
)
