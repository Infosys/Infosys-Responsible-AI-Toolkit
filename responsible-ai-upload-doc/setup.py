from setuptools import find_packages,setup
from pathlib import Path

def get_install_requires() -> list[str]:
    """Returns requirements.txt parsed to a list"""
    fname = Path(__file__).parent / 'requirement/requirements.txt'
    targets = []
    if fname.exists():
        with open(fname, 'r') as f:
            targets = f.read().splitlines()
    return targets

if __name__ == '__main__':
        setup(
            name='responsible-ai-docProcess',
            url="responsible_ai_docProcess",
            packages=find_packages(),
            include_package_data=True,
            python_requires='>=3.6',
            version='0.1.0',
            description='AI Cloud Project Management Services',
            install_requires=get_install_requires(),
            author='amit',
        )
