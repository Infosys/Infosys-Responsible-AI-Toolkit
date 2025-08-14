# responsible-ai-model-detail

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction
The `responsible-ai-model-detail` provides us the workbench to add, update or delete dataset files, tenets, preprocessor and model files.This repository is used for uploading model and data files, after successful uploading of files, we will get IDs generated, which are needed for generating a batch ID based on our tenant, used for performing our tenant's work.


## Installation
To run the application, first we need to install Python and the necessary packages:

1. Install Python (version == 3.11.4) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.

2. Clone the repository:`responsible-ai-model-detail` by executing the command in git bash or cmd:
    ```sh
    git clone <repository-url>
    ```

3. Create a virtual environment by executing this command in cmd:
    ```sh
    python -m venv venv
    ```

4. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
         ```

5. Now navigate to the `responsible-ai-model-detail` directory in cmd::
    ```sh
    cd responsible-ai-model-detail
    ```

6. Go to the `workbench` directory and then `requirements` directory where the `requirement.txt` file is    present and install the requirements:
    
    ```sh
    cd workbench\requirements
    ```
    
    Now install the requirements - 

    ```sh
    pip install -r requirement.txt
    ```
## Set Configuration Variables
After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `app` directory in responsible-ai-model-details repository at path - responsible-ai-model-detail\workbench\src

2. Locate the `.env` file inside app directory, which contains keys like the following:

  ```sh
DB_NAME="${dbname}"
DB_USERNAME="${username}"
DB_PWD="${password}"
DB_IP="${ipaddress}"
DB_PORT="${port}"
MONGO_PATH="mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/"
EXPLAINABILITYGENERATION="${explainabilitygeneration}"
FAIRNESSGENERATION = "${fairnessgeneration}"
SECURITYGENERATION = "${securitygeneration}"
MODEL_CONTAINER_NAME = "${modelcontainername}"
DATA_CONTAINER_NAME = "${datacontainername}"
PREPROCESSOR_CONTAINER_NAME = "${preprocessorcontainername}"
AZURE_UPLOAD_API = "${azureuploadapi}"
AZURE_GET_API = "${azuregetapi}"
AZURE_UPDATE_API = "${azureupdateapi}"
DB_TYPE = "${dbtype}"
COSMOS_PATH = "${cosmospath}"
allow_origin = "${allow_origin}"
allow_methods = "${allow_methods}"
  ```

3. Replace the placeholders with your actual values.

   Give the .env file variables their values as follow -  
```sh
   dbname="enter your mongodb database name"
   username="enter your mongodb username"
   password="enter your mongodb password"
   ipaddress="enter your mongodb IP address"
   port="enter your mongodb port number"
   MONGO_PATH="will get updated itself once above values have been provided"
   explainabilitygeneration="enter rai endpoint for explainabilty report generation"
   fairnessgeneration="enter rai endpoint for fairness report generation"
   securitygeneration="enter rai endpoint to run security attacks"
   modelcontainername="enter your model container name"
   datacontainername="enter your data container name"
   PREPROCESSOR_CONTAINER_NAME="enter preprocessor container name"
   azureuploadapi="enter rai endpoint for azure blob to add file"
   azuregetapi="enter rai endpoint to get blob"
   azureupdateapi="enter rai endpoint to update file"
   dbtype="enter the dbtype, example- if using mongodb give value as `mongo`, if using cosmos db give value as `cosmos`"
   allow_origin="enter the list of origins(urls) that should be permitted to make cross-origin requests."
   allow_methods="enter a list of HTTP methods that should be allowed for cross-origin requests, example - ["GET", "POST", "OPTIONS", "HEAD"]"
   cosmospath="if you are using cosmos db give your cosmos db path"
 ```  

## Running the Application
Once we have completed all the aforementioned steps, we can start the service.

1. Navigate to the `src` directory using cmd

2. Run `main.py` file:
    ```sh
    python main.py
    ```

3. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running:`http://localhost:80/v1/workbench/docs`


## License
The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.


## Contact
If you have more questions or need further insights please feel free to connect with us @ Infosysraitoolkit@infosys.com
