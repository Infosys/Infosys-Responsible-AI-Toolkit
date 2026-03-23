C:\Python\Python310\python.exe -m venv p_env
C:\Python\Python310\python.exe -m pip install --upgrade pip
p_env\Scripts\activate.bat & 
pip install --use-pep517 moviepy rouge-score &
python -m pip install -r requirement.txt
