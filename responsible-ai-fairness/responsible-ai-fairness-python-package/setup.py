import setuptools
setuptools.setup(
                 name='infosys_responsible_ai_fairness',
                 version='1.1.5',
                 description='Responsible AI',
                 long_description='infosys_responsible_ai_fairness',
                 classifiers=['Programming Language :: Python :: 3', 'License :: OSI Approved :: MIT License', 'Operating System :: OS Independent'],
                 package_dir={'': 'infosys_responsible_ai_fairness'},
                 packages=setuptools.find_packages(where='infosys_responsible_ai_fairness'),
                 python_requires='>=3.11',
                 install_requires=['pandas', 'numpy', 'aif360'])