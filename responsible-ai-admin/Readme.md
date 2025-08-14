# Responsible-AI-ADMIN

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction

It is the supporting module which is used for configuring the main module.
User can create recognizer, custom templates, configure Thresholds and map it to created account and portfolio.
 
## Requirements
1. Python 3.9 - 3.11
2. VSCode
3. Mongo DB
 
## Installation

To run the application, first we need to install Python and the necessary packages:
 
1. Install Python (version >= 3.9) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.
 
2. Install MongoDB by following the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/).
 
3. Install `pip` if it is not already installed. You can download and install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/).

4. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

5. Navigate to the `responsible-ai-admin` directory:
    ```sh
    cd responsible-ai-admin
    ```

6. Create a virtual environment:
    ```sh
    python -m venv myenv
    ```

7. Activate the virtual environment:
    - On Windows:
        ```sh
        .\myenv\Scripts\activate
         ```
 
    - On Linux/Mac:
        ```sh
        source myenv/bin/activate
        ```
8. Now go back to `responsible-ai-admin\responsible-ai-admin` to install the requirements by running the following command : 
   ```sh
     cd responsible-ai-admin
     pip install -r .\requirement\requirement.txt
     ```

## Set Configuration Variables
After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `rai_admin` directory:
    ```sh
    cd src/rai_admin
    ```
2. Locate the `.env` file, which contains keys like the following:
   ```sh
      AZUREADDFILE="${azureaddfileurl}"   # [Mandatory for RAG]
      CONTAINERNAME="${containername}"    # [Mandatory for RAG]
      COLLECTIONNAME = "${collectionname}"# [Mandatory for RAG]
      AZUREBLOBNAME = `"http://localhost:[PORT NUMBER]/api/v1/azureBlob/getBlob?"`
      OPENAI_MODEL = "${openaimodel}"
      OPENAI_API_TYPE = "${apitype}"
      OPENAI_API_BASE = "${apibase}"
      OPENAI_API_KEY = "${apikey}"
      OPENAI_API_VERSION = "${apiversion}"

      DB_NAME="${dbname}"                 # [Mandatory] - Any Name : RAI_Admin_DB
      DB_USERNAME="${username}"           # [Optional] 
      DB_PWD="${password}"                # [Optional] 
      DB_IP="${ipaddress}"                # [Optional] 
      DB_PORT="${port}"                   # [Optional] 
      MONGO_PATH="mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/"     # [Mandatory] MONGO_PATH = "mongodb://localhost:[PORT NUMBER]/"  - if using DB_TYPE = "mongo" locally. Also, use the port according your local
      DB_TYPE ="${dbtype}"                # [Mandatory] DB_TYPE = "mongo"
      RAG_IP="${rag_ip}"                  # [Mandatory for RAG]
      COSMOS_PATH ="${cosmos_path}"       # [Optional] - Needed if DB_TYPE = "cosmos"
   ```
   ```sh
    allow_origin = "${allow_origin}"     # allow_origin ="*"         
    To allow access to all sites, use the value *. Alternatively, you can specify a list of sites that should have access.

    allow_method = "${allow_method}"     # allow_method="GET, POST, OPTIONS, HEAD, DELETE, PATCH, UPDATE"
   ```
3. Replace the placeholders with your actual values.

4. Required File storage & Hallucination dependency running in Local
rag_ip= `http://localhost:[PORT_NUMBER]`

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
3. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running: 
    `http://localhost:<portnumber>/api/v1/rai/admin/docs#/`

    User can also change the port which is mentioned in main.py file

NOTE : To use the following API endpoints:

            /api/v1/rai/admin/UpdateOpenAI
            /api/v1/rai/admin/UpdateReminder
            /api/v1/rai/admin/UpdateGoalPriority
            /api/v1/rai/admin/getOpenAI
            /api/v1/rai/admin/userRole
      To use getRole , need to have Authority Table with roles defined
            /api/v1/rai/admin/getRole
            
   Make the following changes :
    1.Create new collection in Db as OpenAIConfig.
    2.Dump the following json in the collection : 
   ```sh
   [{
   "_id": 1697448919.0553722,
   "isOpenAI": true,
   "selfReminder": true,
   "isNemo": true,
   "role": "ROLE_ADMIN",
   "CreatedDateTime": {
     "$date": "2023-10-16T09:35:19.055Z"
   },
   "LastUpdatedDateTime": {
     "$date": "2023-10-16T09:35:19.055Z"
   },
   "goalPriority": true
   },
   {
     "_id": 1697448919.0572698,
     "isOpenAI": true,
     "selfReminder": true,
     "isNemo": true,
     "role": "ROLE_USER",
     "CreatedDateTime": {
       "$date": "2023-10-16T09:35:19.057Z"
     },
     "LastUpdatedDateTime": {
       "$date": "2023-10-16T09:35:19.057Z"
     },
     "goalPriority": true
   }]
   ```

## License

The source code for the project is licensed under the MIT license, which you can find in the [License.md](License.md) file.

## Contact
If you have more questions or need further insights please feel free to connect with us at
DL : Infosys Responsible AI
Mailid: Infosysraitoolkit@infosys.com

### Known Issue:
Below mentioned endpoints will not work in the current release
1. RAG-setCache/api/v1/rai/admin/setCache
2. RAG-getEmbedings	/api/v1/rai/admin/getEmbedings
3. RAG-clearEmbedings	/api/v1/rai/admin/clearEmbedings
4. RAG-deleteFile	/api/v1/rai/admin/deleteFile
