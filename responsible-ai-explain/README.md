# Responsible-AI-Explain

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction

**Explainability** offers comprehensive explanations for traditional machine learning and deep learning models. It supports both local and global explainable AI methods, including anchors and feature importance, across classification, regression, and time series tasks. This ensures transparency and insight into model behavior, facilitating better decision-making and trust.

## Features

**Types of Explainability**

Explainability methods can be broadly categorized into **Local** and **Global** approaches.

**Local Explainability**
focuses on explaining individual predictions made by a model. It helps users understand why a particular decision was made in a specific instance. Some popular local explainability methods include:

- **LIME (Local Interpretable Model-agnostic Explanations):**

    - **How it works**: LIME approximates the complex model with a simpler, interpretable model (like a linear model) locally around the instance of interest. It perturbs the input data and observes how the model's predictions change to understand which features are important for the prediction.

**Global Explainability**
aims to provide a comprehensive understanding of the overall behavior and structure of a model. It helps in understanding how the model generally makes decisions across the entire dataset. Some global explainability methods include:

- **SHAP (SHapley Additive exPlanations):**

    - **How it works**: SHAP values are derived from cooperative game theory, where the importance of each feature is determined based on its contribution to the prediction, considering all possible combinations of features.

## Installation
To run the application, first we need to install Python and the necessary packages:

1. Install Python (version 3.11.x) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.

2. Install MongoDB by following the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/).
    ### Importing JSON Data into MongoDB

    1. Ensure MongoDB is running on your system. Open a command prompt and start MongoDB using the following command:
        ```sh
        mongod
        ```

    2. Import your JSON data into MongoDB:

        **Using MongoDB Compass**
        1. Open MongoDB Compass:
            - Launch MongoDB Compass on your machine.
        2. Connect to Your MongoDB Instance:
            - Enter your connection string as `mongodb://localhost:27017/` and click **Connect**.
        3. Create a New Database and Collection:
            - Click on the **Create Database** button.
            - Enter your database name (it can be anything) and collection name as **Tbl_Explanation_Methods**, then click **Create Database**.
        4. Import JSON Data:
            - Navigate to the newly created collection.
            - Click on the **Add Data** button and select **Import File**.
            - Choose the **Tbl_Explanation_Methods.json** file located in the **responsible-ai-explain/docs** folder.
            - Select **JSON** as the file type and click **Import**.

    3. Ensure the same database name is added to the `RAI_EXPLAIN_DB` configuration variable in your `.env` file:
        ```sh
        RAI_EXPLAIN_DB=<database>
        ```

3. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

4. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

5. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
         ```

6. Upgrade `pip`:
    ```sh
    python -m pip install --upgrade pip
    ```

7. Navigate to the `responsible-ai-explain` directory:
    ```sh
    cd responsible-ai-explain
    ```

8. Go to the `requirements` directory where the `requirement.txt` file is present and install the requirements:
    ```sh
    cd responsible-ai-explain\requirements
    pip install -r requirement.txt
    ```

**Note:** 
Ensure you install versions of the packages that are compatible with your operating system and python environment.
 
## Dependencies
The Explainability APIs depend on both the Model Details (responsible-ai-model-detail) repository and the Reporting Tool (responsible-ai-reporting-tool) repository. Please follow the setup instructions in the README files of both repositories to configure them. Ensure that both services are up and running before interacting with the Explainability APIs.
    
## Set Configuration Variables

After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `explain` directory:
    ```sh
    cd ..
    cd src/explain
    ```

2. Locate the `.env` file in the project directory. This file contains several configuration keys. Make sure to fill in the mandatory fields as shown below (sample values are provided for reference):

    ```sh
    RAI_EXPLAIN_DB = "${rai_explain_db}"      # [Mandatory] RAI_EXPLAIN_DB = "RAI_Explain_DB"
    DB_NAME = "${dbname}"                     # [Mandatory] DB_NAME = "Rai_Usecase_DB"
    DB_USERNAME = "${username}"               # [Optional]
    DB_PWD = "${password}"                    # [Optional]
    DB_IP = "${ipaddress}"                    # [Optional]
    DB_PORT = "${port}"                       # [Optional]
    DB_TYPE ="${dbtype}"                      # [Mandatory] DB_TYPE = "mongo"
    MONGO_PATH = "mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/"    # [Mandatory] MONGO_PATH = "mongodb://localhost:27017/"
    VERIFY_SSL = "${sslVerify}"             # [Mandatory] VERIFY_SSL = "False"
    COSMOS_PATH = "${cosmos_path}"            # [Optional]
    ```
    ```sh
    ALLOWED_ORIGINS= "${allowed_origins}"     # ALLOWED_ORIGINS ="*"         
    To allow access to all sites, use the value *. Alternatively, you can specify a list of sites that should have access.
    ```
     ```sh
    REPORT_URL = "${reporturl}"               # [Mandatory] REPORT_URL = "http://localhost/v1/report/htmltopdfconversion"  
    You can obtain this from the reporting tool repository. Ensure that the reporting tool is running and you use the same database name for that repository,specifically `DB_NAME = ${dbname}`. 
    You should use the same database name in the explain, reporting tool and model deatils repository.
    ```

3. Replace the placeholders with your actual values.

4. Adding New Environment Variables in Windows
    1. Search for Environment Variables:

        - Type **Environment Variables** in the Windows search bar and select "Edit the system environment variables for your account

    1. In the Environment Variables window, under "User variables" click "New."

        - Variable name: **ACCESS_KEY**
        - Variable value: use any dummy value like ABC
        - Click OK.

    2. Repeat the process for the second variable:

        - Variable name: **SECRET_KEY**
        - Variable value: use any dummy value like XYZ
        - Click OK.

    3. Confirm Changes:

        - Click OK on all windows to close them.

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

3. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running: `http://localhost:<Port_No>/rai/v1/explainability/docs`

For API calls, please refer to the [API Documnet](responsible-ai-explain/docs/API_Doc.pdf)

  
## License

The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.

## Contact

If you have more questions or need further insights, feel free to Connect with us @ infosysraitoolkit@infosys.com
