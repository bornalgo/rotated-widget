from setuptools import setup, find_packages

setup(
    name='rotated-widget',
    version='1.0.0',
    description='A Qt-based widget wrapper that rotates a widget at a specified angle',
    author='Borna Ghannadi',
    author_email='bornalgo@github.com',
    url='https://github.com/bornalgo/rotated-widget.git',
    packages=find_packages(),
    install_requires=['PySide2'],  # Adjust if using PySide6/PyQt6/PyQt5/PyQt4/PySide
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)