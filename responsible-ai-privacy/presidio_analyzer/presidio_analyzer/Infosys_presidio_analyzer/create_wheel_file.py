__copyright__ = """ 2020 - 2021 Infosys Limited, Bangalore, India. All Rights Reserved.  
Version: 2.5.0.0 
Except for any free or open source software components embedded in this Infosys proprietary software program (“Program”), this Program is protected by copyright laws, international treaties and other pending or existing intellectual property rights in India, the United States and other countries.
Except as expressly permitted, any unauthorized reproduction, storage, transmission in any form or by any means (including without limitation electronic, mechanical, printing, photocopying, recording or otherwise), or any distribution of this Program, or any portion of it, may result in severe civil and criminal penalties, and will be prosecuted to the maximum extent possible under the law.
"""
import yaml
import subprocess
import os
with open(r'.\build_config.yaml') as build_file:
    build_config_list = yaml.safe_load(build_file)


for build_config in build_config_list:

    try:
        print(build_config)

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
                )"

            with open('setup.py','w') as file:
                file.write(setup_str)

            subprocess.run(["python", "-m","build"])
            wheel_file = f"{build_config['name']}-{build_config['version']}_build_{build_config['build']}-py3-none-any.whl"
            print(f"wheel_file: {wheel_file}")
            subprocess.run(["python", "-m", "pyc_wheel", f"dist\{wheel_file}"])
        else:
            print(f"Path does not exist ./{build_config['packages']}")
    except Exception as e:
        print("Exception occurred")
