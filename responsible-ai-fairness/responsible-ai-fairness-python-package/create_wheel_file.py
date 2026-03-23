"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import yaml
import subprocess
import os
from fairness.config.logger import CustomLogger

log = CustomLogger()

with open(r'.\build_config.yaml') as build_file:
    build_config_list = yaml.safe_load(build_file)

with open('requirements.txt') as f:
    required = f.read().splitlines()

for build_config in build_config_list:

    try:

        if os.path.exists(f"./{build_config['packages']}"):

            setup_str = f"import setuptools\r" \
                        f"setuptools.setup(\r \
                name='{build_config['name']}',\r \
                version='{build_config['version']}',\r \
                author='{build_config['author']}',\r \
                author_email='{build_config['author_email']}',\r \
                description='{build_config['description']}',\r \
                long_description='{build_config['long_description']}',\r \
                classifiers={build_config['classifiers']},\r \
                package_dir={build_config['package_dir']},\r \
                packages=setuptools.find_packages(where='{build_config['packages']}'),\r \
                python_requires='{build_config['python_requires'][0]}',\r \
                install_requires={required})"

            with open('setup.py','w') as file:
                file.write(setup_str)

            subprocess.run(["python", "-m","build"])
            wheel_file = f"{build_config['name']}-{build_config['version']}_build_{build_config['build']}-py3-none-any.whl"
            # subprocess.run(["python", "-m", "pyc_wheel", f"dist\{wheel_file}"])
        else:

    except Exception as e:
        log.error(e)
