# responsible-ai-red-teaming

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction
The `responsible-ai-red-teaming` repository is designed to enhance the evaluation and security of Large Language Models (LLMs) through a comprehensive suite of red teaming practices. This repository offers a variety of techniques aimed at identifying vulnerabilities and ensuring robust performance in both endpoint and subscription-based LLMs.

One of the key components of this suite is Prompt Automatic Iterative Refinement (PAIR). Inspired by social engineering tactics, PAIR is an innovative algorithm that facilitates the generation of semantic jailbreaks using only black-box access to an LLM. It leverages an attacker LLM to automatically produce jailbreak prompts for a targeted LLM, eliminating the need for human intervention.

In addition to PAIR, the repository features TAP, a query-efficient method for jailbreaking black-box LLMs, along with various other techniques designed for comprehensive evaluation and testing.

By utilizing these advanced methodologies, the `responsible-ai-red-teaming` repository aims to promote responsible AI practices and enhance the resilience of LLMs against potential adversarial attacks.

## Installation
To run the application, follow these steps:

1. **Install Python**: Ensure Python (version == 3.11 or above) is installed from the [official website](https://www.python.org/downloads/) and added to your system PATH.

2. **Clone the Repository**: Clone the `responsible-ai-red-teaming` repository by executing the following command:
    ```sh
    git clone <repository-url>
    ```

3. **Create a Virtual Environment**: Navigate to the cloned repository and create a virtual environment:
    ```sh
    cd responsible-ai-red-teaming
    python -m venv venv
    ```

4. **Activate the Virtual Environment**:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

5. **Install Requirements**: Navigate to the `requirements` directory and install the necessary packages:
    ```sh
    cd redteaming\requirements
    pip install -r requirement.txt
    ```

## Set Configuration Variables
After installing the required packages, configure the necessary environment variables.

1. **Navigate to the `app` Directory**: Go to the `app` directory in the `responsible-ai-red-teaming` repository:
    ```sh
    cd ..\src\app
    ```

2. **Update the [.env](http://_vscodecontentref_/0) File**: Locate the [.env](http://_vscodecontentref_/1) file and update the following keys with your configuration:
    ```properties
    # for dev deployment
    AZURE_GPT4_API_BASE="${apibase_gpt4}"
    AZURE_GPT4_API_VERSION="${apiversion_gpt4}"
    AZURE_GPT4_MODEL_NAME="${modelname_gpt4}"
    AZURE_GPT4_API_KEY="${apikey_gpt4}"
    AZURE_GPT3_API_BASE="${apibase_gpt3}"
    AZURE_GPT3_API_VERSION="${apiversion_gpt3}"
    AZURE_GPT3_MODEL_NAME="${modelname_gpt3}"
    AZURE_GPT3_API_KEY="${apikey_gpt3}"
    allow_origin="${allow_origin}"
    allow_methods="${allow_methods}"
    GOOGLE_API_KEY="${google_api_key}"
    MODERATION_API="${moderation_api}"
    sslVerify = "${sslVerify}"
    DB_NAME = "${db_name}"
    MONGO_PATH="${mongo_path}"
    DB_TYPE = "${db_type}"
    AZURE_GET_API = "${azure_get_api}"
    AZURE_UPLOAD_API = "${azureuploadapi}"
    DATA_CONTAINER_NAME = "${datacontainername}"
    PDF_CONTAINER_NAME = "${pdf_container_name}"
    ```

## Running the Application
Once all the steps above are completed, you can start the service.

1. **Navigate to the `src` Directory**: Use the following command to navigate to the `src` directory where `main.py` exists:
    ```sh
    cd ..\src
    ```

2. **Run the `main.py` File**: Execute the following command to start the application:
    ```sh
    python main.py
    ```

3. **Access the Swagger UI**: Open the following URL in your browser to access the Swagger UI, Replace <portnumber> with the actual port number your application is running on:
 `http://localhost:<portnumber>/v1/redteaming/docs#`

## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.md](License.md ) file.

## Contact
If you have more questions or need further insights, please feel free to connect with us at infosysraitoolkitt@infosys.com.
