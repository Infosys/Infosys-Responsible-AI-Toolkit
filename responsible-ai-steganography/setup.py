"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from setuptools import find_packages, setup
from pathlib import Path


def get_install_requires() -> list:
    """Returns requirements.txt parsed to a list"""
    fname = Path(__file__).parent / 'requirements/requirements.txt'
    targets = []
    if fname.exists():
        with open(fname, 'r') as f:
            targets = f.read().splitlines()
        # Filter out comments and development dependencies
        targets = [line.strip() for line in targets 
                  if line.strip() and not line.startswith('#') 
                  and not line.startswith('pytest') 
                  and not line.startswith('black')
                  and not line.startswith('flake8')
                  and not line.startswith('mypy')
                  and not line.startswith('sphinx')]
    return targets


if __name__ == '__main__':
    setup(
        name='responsible-ai-steganography',
        url="responsible-ai-steganography",
        packages=find_packages(),
        include_package_data=True,
        python_requires='>=3.11',
        version='1.0.0',
        description='AI Text Steganography Detection Service - part of Infosys Responsible AI Toolkit',
        long_description='A comprehensive service for detecting various forms of text-based steganographic attacks including zero-width characters, whitespace manipulation, linguistic steganography, and Unicode exploitation.',
        install_requires=get_install_requires(),
        author='Infosys Responsible AI Team',
        license='MIT',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.11',
            'Topic :: Security',
            'Topic :: Text Processing',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
        keywords='steganography detection security ai responsible-ai text-analysis',
    )
