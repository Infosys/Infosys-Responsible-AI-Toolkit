
## Workbench

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Database Setup Guide](#database-setup-guide)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Set Configuration Variables](#set-configuration-variables)
- [License](#license)
- [Contact](#contact)
  
## Introduction
The workbench repository is used for processing and generating report for Unstructured text .

## Prerequisites
1. Before installing the repo for Workbench, first you need to install the repos for Responsible AI File Storage, Privacy,Moderation layer, Explainability and Safety . 
Please find the link for Responsible AI File Storage repo : [File Storage repo](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/tree/master/responsible-ai-file-storage). 
Please find the link for Responsible AI Privacy repo : [Privacy repo](https://github.com/Infosys-AI-Cloud-MMS/responsible-ai-privacy) 
Please find the link for Responsible AI Safety repo : [Safety repo](https://github.com/Infosys-AI-Cloud-MMS/responsible-ai-safety)
Please find the link for Responsible AI Moderation layer repo : [Moderation layer repo](https://github.com/Infosys-AI-Cloud-MMS/responsible-ai-fm-ext-flask)
Please find the link for Responsible AI Explainability repo : [Explainability repo](https://github.com/Infosys-AI-Cloud-MMS/responsible-ai-explain)

2. **Installation of Python** : Install Python (version 3.11.x) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.


3. **Installation of pip** :

**Linux:**
1. Check if pip is already installed: Open a terminal and run the following command:
```sh
pip --version
```
2. If pip is not installed, you'll see an error message.
3. Install pip using get-pip.py: Download the `get-pip.py` script as follows
```sh
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```
4. Make the script executable:
```sh
chmod +x get-pip.py
```
5. Run the script:
```sh
./get-pip.py
```
6. This will install pip and its dependencies.

**Windows:**
1. Download the Python installer: Visit the official [Python website](https://www.python.org/downloads/) and download the latest Python installer for Windows.

2. Install Python: Run the installer and follow the on-screen instructions. Make sure to check the "Add Python to PATH" option during the installation.

3. Verify pip installation: Open a command prompt and run the following command:
```sh
pip --version
```
If pip is installed, you'll see its version.


**macOS:**

**Approach 1**
1. Check if pip is already installed: Open a Terminal window.Type
```sh 
pip --version
```
and press Enter. If pip is installed, you'll see its version.

2. Install pip using Homebrew (recommended): If pip isn't installed or you're unsure, install `Homebrew`, a popular package manager for macOS:
```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"   
```
3. Once Homebrew is installed, use it to install pip:
```sh
brew install python
```
4. Verify the installation: Type 
```sh
pip --version
```
again.You should see the installed version of pip.

**Approach 2**

If you encounter issues or prefer a manual installation:

1. Download the get-pip.py script : Use curl to download the script:
```sh
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```
2. Run the script : Make sure you're using the correct Python interpreter (usually python3):
```sh
python3 get-pip.py
```
3. Enter your password (if prompted) : When you run the script, you might be prompted for your administrator password. This is because the installation process requires elevated privileges. Type your password and press Enter (the characters won't be displayed for security reasons).

4. Verify the installation : Once the script finishes running, you can verify that pip is installed by typing:
```sh
pip --version
```
If pip is installed correctly, you should see the installed version number displayed.

## Requirements
Python 3.9 - 3.11
VSCode
MongoDB / CosmosDB (NOTE : Get setup for any of the one DB Type from below section)

## Installation

### Steps for Installation :

**Step 1**  : Clone the repository `responsible-ai-workbench`:
```sh
git clone <repository-url>
```

**Step 2**  : Navigate to the `responsible-ai-workbench` directory:
```sh
cd responsible-ai-workbench
```

**Step 3**  : Activate the virtual environment for different OS.

**Windows:**
1. Open Command Prompt or PowerShell: Find and open the appropriate command-line interface
2. Create a virtual environment using the following python command :
```sh
> python -m venv <Name of your Virtual Environment>
```
Let's say your virtual env. name is `myenv` and is located in `C:\Users\your_username`

3. Navigate to the virtual environment directory and activate it using below command :
```sh
> cd C:\Users\your_username\myenv\Scripts
> .\activate
```
4. You should see a prompt that indicates the activated environment, such as (myenv) before your usual prompt like this :
```sh
(myenv) C:\Users\your_username\myenv\Scripts>
```
**Linux:**
1. Open a terminal: Find and open a terminal window.
2. To create a virtual environment, install the relevant version of the `venv` module.Since we are using Python 3.11, install the 3.11 variant of the package, which is named python3.11-venv
```sh
abc@demo:~/$ sudo apt install python3.11-venv
```
3. Create a Virtual env like this.
```sh
abc@demo:~/Projects/MyCoolApp$ python3.11 -m venv <Name of your Virtual Environment>
```
Let's say your virtual env. name is `myenv`

4. Activate the environment: Run the following command
```sh
abc@demo:~/Projects/MyCoolApp$ source myenv/bin/activate
```
5. You should see a prompt that indicates the activated environment, such as (myenv) before your usual prompt like this :
```sh
(myenv) abc@demo:~/Projects/MyCoolApp$
```

**MacOS:**
1. Open Terminal: Find and open the Terminal.
2. Activate the environment: Run the following commands
```sh
python3 -m pip install virtualenv
python3 -m virtualenv <Name of your Virtual environment>
```
Let's say, your virtual env name is `myenv`.
```sh 
source ./myenv/bin/activate 
```


**Step 4** : Go to the `requirement` directory where the `requirements.txt` file is present :

Install the requirements as shown below :
```sh
pip install -r requirements.txt
```

## Database Setup Guide

### MongoDB Setup (Local)

1. **Download and Install MongoDB Community Edition**
   - Visit the [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Select your operating system and download the installer
   - Follow the installation wizard instructions

2. **Start MongoDB Service**
   - **Windows**:
     ```
     "C:\Program Files\MongoDB\Server\{version}\bin\mongod.exe" --dbpath="c:\data\db"
     ```
   - **Linux/macOS**:
     ```
     mongod --dbpath /data/db
     ```

3. **Connect to MongoDB**
   - **Windows**: Open a new command prompt and run:
     ```
     "C:\Program Files\MongoDB\Server\{version}\bin\mongo.exe"
     ```
   - **Linux/macOS**:
     ```
     mongo
     ```

### Azure Cosmos DB Setup (Local Emulator)

1. **Download and Install the Azure Cosmos DB Emulator**
   - Visit [Azure Cosmos DB Emulator](https://aka.ms/cosmosdb-emulator)
   - Download and install the emulator

2. **Start the Emulator**
   - **Windows**: Search for "Azure Cosmos DB Emulator" in the Start menu and open it
   - The emulator will start and open a web browser at `https://localhost:8081/_explorer/index.html`
   - Accept the self-signed certificate prompt

3. **Get Connection String**
   - In the emulator, click on "Tools" on the left sidebar
   - Copy the Primary Connection String

## Running the Application

Once we have completed all the aforementioned steps, we can start the service.

1. Navigate to the `src` directory:
    ```sh
    cd ..
    ```

2. Run `main.py` file:
    ```sh
    python main.py
     ```
3. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running:`http://localhost:30080/v1/questionnaire/docs`

    User can also change the port which is mentioned in main.py file



## Set Configuration Variables
After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `responsible-ai-workbench/src
2. Locate the `.env` file, which contains keys like the following:
```sh
DB_NAME="${dbname}" # [Mandatory] Any Name : RAI_Questionnare_DB
PRIVACY_API="${privacyapi}" # [Mandatory]
PROFANITY_API="${profanityapi}" # [Mandatory]
FM_MODERATION_API="${fmmoderationapi}" # [Mandatory]
EXPLAINABILITY_API="${explainabilityapi}" # [Mandatory]
SERVERTYPE="${servertype}" # [Mandatory]
DB_USERNAME="${username}" # [Optional]
DB_PWD="${password}" # [Optional]
DB_IP="${ipaddress}" # [Optional]
DB_PORT="${port}" # [Optional]
MONGO_PATH="mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/" # MONGO_PATH = "mongodb://localhost:27017/"  - if using DB_TYPE = "mongo" locally. Also, use the port according your local
DB_TYPE ="${dbtype}" # [Mandatory] DB_TYPE = "mongo", "cosmos"
COSMOS_PATH ="${cosmos_path}" # [Optional] - Needed if DB_TYPE = "cosmos"
allow_origin = "${allow_origin}" # [Mandatory]
allow_method = "${allow_method}" # [Mandatory]
VERIFY_SSL="${verify_ssl}" # [Mandatory]

```

## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE](License.md) file.

## Contact
If you have more questions or need further insights please feel free to connect with us at
DL : Infosys Responsible AI
Mailid: Infosysraitoolkit@infosys.com

 
