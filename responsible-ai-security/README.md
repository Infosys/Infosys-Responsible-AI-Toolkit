## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction
**ML Security** provides the report for Traditional ML Model using different categories of attacks such as Evasion, poisioning as well as inference. It evaluates the Models with different attacks and provide a mechanishm to stregthen the model if model is found vulnerable.

## Features
Different types of attacks are supported as:-
- **Evasion Attacks** : Evasion attacks are a type of adversarial attack aimed at deceiving ML Model by manipulating input data in a way that causes the AI to misclassify or make incorrect predictions, while appearing normal to humans.
- **Poisioning Attacks** : Poisoning attacks are a type of adversarial attack that aim to corrupt the training data used to build an AI model, leading to the model's inaccurate predictions or biased behavior.
- **Inference Attacks** : Inference attacks are a type of adversarial attack that aim to extract sensitive information from an AI model, even though the model itself is not directly compromised. this attacks also led to model thieft.
- **Adversarial Data** : In ML, adversarial data refers to deliberately crafted input data designed to mislead or trick an ML model into making incorrect predictions or classifications. This data is specifically designed to exploit vulnerabilities in the model's decision-making process, leading to unexpected or harmful outcomes.
- **Defense Model** : Here, defense model refers to a technique or strategy designed to protect ML Model from adversarial attacks. These attacks aim to manipulate or exploit vulnerabilities in ML Model, leading to incorrect predictions, biased outputs, or even complete system failure.

## Installation
To run the application, first we need to install Python and the necessary packages:

1. Install Python (version == 3.11.4) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.

2. Install MongoDB by following the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/).

3. Install `pip` if it is not already installed. You can download and install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/).

4. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

5. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

6. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
         ```
    - On Linux/Mac:
        ```sh
        source venv/bin/activate
        ```

7. Navigate to the `Responsible-AI-Security-API` directory:
    ```sh
    cd Responsible-AI-Security-API
    ```

8. Navigate to `src` directory:
    ```sh
    cd wrapper\app\src 
    ```

9. Go to the `requirements` directory where the `requirement.txt` file is present
    - If On Windows:
        Do the needful as written in the end section of file
    - Now, install the requirements:
        ```sh
        pip install -r ../requirements/requirement.txt
        ```

## Set Configuration Variables
After installing all the required packages, configure the variables necessary to run the APIs.

1. Locate the `.env` file in app folder, which contains keys like the following:

    ```sh
    AUTH_TYPE=  "${authtype}"                                 # [Mandatory] AUTH_TYPE=  "azure" # Options: azure,jwt,none
    SECRET_KEY="${secretkey}"                                 # [Mandatory]
    AZURE_CLIENT_ID= "${azureclientid}"                       # [Mandatory]
    AZURE_TENANT_ID="${azuretenantid}"                        # [Mandatory]
    AZURE_AD_JWKS_URL="${azuread_jwks_url}"                   # [Mandatory]

    ALLOW_ORIGINS ="${allow_origins}"                         # [Mandatory] ALLOW_ORIGINS="*"  
    ERRORLOGAPI = "${errorlogapi}"                            # [Mandatory] ERRORLOGAPI=""
    TELEMETRY_FLAG = "${telemetry_flag}"                      # [Mandatory] TELEMETRY_FLAG ="False"
    SECURITYPDFGENERATIONIP = "${ip}"                         # [Mandatory] SECURITYPDFGENERATIONIP='http://localhost:80'
    DB_NAME="${dbname}"                                       # [Mandatory] DB_NAME="rai_repository"  
    DB_TYPE="${dbtype}"                                       # [Mandatory] DB_TYPE = "mongo"

    DB_USERNAME="${username}"                                 # [Optional]
    DB_PWD="${password}"                                      # [Optional]
    DB_IP="${ipaddress}"                                      # [Optional]
    DB_PORT="${port}"                                         # [Optional]
    MONGO_PATH="mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/"  # [Mandatory] MONGO_PATH = "mongodb://localhost:27017/"
    
    ```
    ```sh
    To allow access to all sites, use the value *. Alternatively, you can specify a list of sites that should have access.
    Also to avoid auhthentication, use AUTH_TYPE as "none". Alternatively, you can use jwt as well as azure authantication system by passing different supported keys.
    ```

2. Replace the placeholders with your actual values.

## Running the Application
Once we have completed all the aforementioned steps, we can start the service.

1. Run `main.py` file:
    ```sh
    python main.py
    ```

2. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running:`http://localhost:80/rai/v1/security_workbench/docs`

## License
The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](License.md) file.

## Open Source tools Used:
adversarial-robustness-toolbox : https://github.com/Trusted-AI/adversarial-robustness-toolbox


## Contact
If you have more questions or need further insights, feel free to Connect with us @ Infosysraitoolkit@infosys.com
