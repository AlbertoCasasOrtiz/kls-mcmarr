from setuptools import setup, find_packages

setup(
    name='kls_mcmarr',
    version='1.2.10',
    description='Implementation of KLS processing pipeline following MCMARR framework.',
    author='Alberto Casas Ortiz',
    author_email='albertocasasortiz@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'mediapipe',
        'opencv-python',
        'pandas',
        'numpy',
        'scipy',
        'matplotlib',
        'dtw-python',
        'pyttsx3',
        'openpyxl',
        'tensorflow'
    ],
)
