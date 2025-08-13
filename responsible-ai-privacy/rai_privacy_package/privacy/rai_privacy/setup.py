import setuptools
from setuptools import find_packages,setup
from pathlib import Path
def get_install_requires() -> list[str]:
      fname = Path(__file__).parent / 'requirements/requirement.txt'
      targets = []
      if fname.exists():
          with open(fname, 'r') as f:
              targets = f.read().splitlines()
      return targets
setuptools.setup(
                 name='privacy',
                 version='1.0.2',
                 author='Amit Hegde',
                 author_email='amitumamaheshwar.h@infosys.com',
                 description='Infosys PII Analyzation & Anonymization System',
                 long_description='Infosys PII Analyzation & Anonymization System',
                 classifiers=['Programming Language :: Python :: 3', 'License :: OSI Approved :: MIT License', 'Operating System :: OS Independent'],
                 package_dir={'': 'privacy'},
                 packages=setuptools.find_packages(where='privacy'),
                 python_requires='>=3.6',
                 install_requires=['fastapi', 'pydantic', 'pymongo', 'python-dotenv', 'uvicorn', 'pandas', 'openpyxl', 'xlsxwriter', 'presidio_anonymizer', 'presidio_image_redactor==0.0.48', 'python-multipart', 'pyyaml', 'regex', 'opencv-python-headless', 'omegaconf', 'anyio', 'blis', 'catalogue', 'certifi', 'charset-normalizer', 'click', 'colorama', 'confection', 'contourpy', 'cycler', 'cymem', 'fastapi', 'FastAPI-SQLAlchemy', 'filelock', 'fonttools', 'diffprivlib', 'greenlet', 'h11', 'idna', 'Jinja2', 'kiwisolver', 'langcodes', 'MarkupSafe', 'matplotlib', 'murmurhash', 'numpy', 'packaging', 'pathy', 'phonenumbers', 'Pillow', 'pip', 'preshed', '#presidio-analyzer', 'presidio-anonymizer', 'presidio-image-redactor==0.0.48', 'pycryptodome', 'pydantic', 'pydicom', 'pyparsing', 'pypng', 'pytesseract', 'python-dateutil', 'python-multipart', 'PyYAML', 'regex', 'requests', 'requests-file', 'setuptools', 'six', 'smart-open', 'sniffio', 'spacy', 'spacy-legacy', 'spacy-loggers', 'SQLAlchemy', 'srsly', 'starlette', 'thinc', 'tldextract', 'tqdm', 'typer', 'typing_extensions', 'urllib3', 'uvicorn', 'wasabi', 'httpx', 'opencv-python-headless', 'numpy', '# numpy>=1.18.5', '# opencv-python>=4.1.1', '# Pillow>=7.1.2', 'PyYAML>=5.3.1', 'requests>=2.23.0', 'scipy>=1.4.1', 'torch>=1.7.0,!=1.12.0', 'torchvision>=0.8.1,!=0.13.0', 'tqdm>=4.41.0', 'protobuf<4.21.3', '# Logging -------------------------------------', 'tensorboard>=2.4.1', '# wandb', '', '# Plotting ------------------------------------', '# pandas>=1.1.4', 'seaborn>=0.11.0', '', '# Export --------------------------------------', '# coremltools>=4.1  # CoreML export', '# onnx>=1.9.0  # ONNX export', '# onnx-simplifier>=0.3.6  # ONNX simplifier', '# scikit-learn==0.19.2  # CoreML quantization', '# tensorflow>=2.4.1  # TFLite export', '# tensorflowjs>=3.9.0  # TF.js export', '# openvino-dev  # OpenVINO export', '', '# Extras --------------------------------------', 'ipython  # interactive notebook', 'psutil  # system utilization', 'thop  # FLOPs computation', '#https://huggingface.co/spacy/en_core_web_lg/resolve/main/en_core_web_lg-any-py3-none-any.whl', '# lib/presidio_analyzer-4.1.0-py3-none-any.whl', '# lib/aicloudlibs-0.1.0-py3-none-any.whl', '# lib/en_core_web_lg-any-py3-none-any.whl', '', '# Usage: pip install -r requirements.txt', 'easyocr', '# Base ----------------------------------------', '# matplotlib>=3.2.2', 'numpy>=1.18.5', '# opencv-python>=4.1.1', '# Pillow>=7.1.2', 'PyYAML>=5.3.1', 'requests>=2.23.0', 'scipy>=1.4.1', 'torch>=1.7.0,!=1.12.0', 'torchvision>=0.8.1,!=0.13.0', 'tqdm>=4.41.0', 'protobuf<4.21.3', '', '# Logging -------------------------------------', 'tensorboard>=2.4.1', '# wandb', '', '# Plotting ------------------------------------', '# pandas>=1.1.4', 'seaborn>=0.11.0', '', '# Export --------------------------------------', '# coremltools>=4.1  # CoreML export', '# onnx>=1.9.0  # ONNX export', '# onnx-simplifier>=0.3.6  # ONNX simplifier', '# scikit-learn==0.19.2  # CoreML quantization', '# tensorflow>=2.4.1  # TFLite export', '# tensorflowjs>=3.9.0  # TF.js export', '# openvino-dev  # OpenVINO export', '', '# Extras --------------------------------------', 'ipython  # interactive notebook', 'psutil  # system utilization', 'thop  # FLOPs computation', '# albumentations>=1.0.3', '# pycocotools>=2.0  # COCO mAP', '# roboflow', '', '# code pii', 'regex', 'tqdm', 'pandas', 'datasets', 'detect_secrets', 'gibberish_detector', 'huggingface_hub', 'nltk', 'scikit-learn', 'seqeval', 'transformers', 'datasets', 'transformers', 'evaluate', 'seqeval', 'autopep8', '', '# face detection', 'tensorflow', '', '', '', ''],
                include_package_data=True,
                 package_data={'': ['*.ini', '*.pt', '*.dcm', '*.xml', '*.env']},
                 )