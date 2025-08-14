# Responsible-AI-LLM

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction

**LLM** provides an implementation for generating images using a Large Language Model (LLM). It demonstrates how natural language prompts can be interpreted and transformed into visual content through model pipelines that integrate natural language understanding with image synthesis. Additionally, the repository includes endpoint for interacting with LLMs—specifically OpenAI’s services.

## Features
- **Natural Language to Image Generation with DALL·E**  
  Generate high-quality images from textual prompts using OpenAI’s DALL·E model, which translates language into coherent visual scenes.
- **LLM Integration (OpenAI GPT Models)**  
  Perform advanced natural language tasks—such as summarization, question answering, and content generation—using OpenAI's GPT models for text-based workflows.

## Installation
To run the application, first we need to install Python and the necessary packages:

1. Install Python (version 3.11.x) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.

2. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

3. Navigate to the `responsible-ai-llm` directory:
    ```sh
    cd responsible-ai-llm
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

6. Go to the `requirements` directory where the `requirement.txt` file is present and install the requirements:
    ```sh
    pip install -r requirement.txt
    ```

## Set Configuration Variables

After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `llm` directory:
    ```sh
    cd ..
    cd src/llm
    ```

2. Locate the `.env` file, which contains keys like the following:

    ```sh
    ALLOWED_ORIGINS = "${allowed_origins}"
    OPENAI_API_TYPE = "${apitype}"                           # [Mandatory] OPENAI_API_TYPE = "azure"
    OPENAI_API_BASE_GPT3 = "${apibase_gpt3}"
    OPENAI_API_KEY_GPT3 = "${apikey_gpt3}"
    OPENAI_API_VERSION_GPT3 = "${apiversion_gpt3}"                
    OPENAI_MODEL_GPT3 = "${openaimodel_gpt3}"
    OPENAI_API_BASE_GPT4 = "${apibase_gpt4}"
    OPENAI_API_KEY_GPT4 = "${apikey_gpt4}"
    OPENAI_API_VERSION_GPT4 = "${apiversion_gpt4}"  
    OPENAI_MODEL_GPT4 = "${openaimodel_gpt4}"
    OPENAI_API_BASE_GPT4_O = "${api_base}"
    OPENAI_API_KEY_GPT4_O = "${api_key}"
    OPENAI_API_VERSION_GPT4_O = "${api_version}"  
    OPENAI_MODEL_GPT4_O = "${model}"
    AZURE_OPENAI_API_KEY_DALL_E_2 = "${azure_openai_api_key_dall_e_2}"
    AZURE_OPENAI_ENDPOINT_DALL_E_2 = "${azure_openai_endpoint_dall_e_2}"
    AZURE_OPENAI_API_VERSION_DALL_E_2 = "${azure_openai_api_version_dall_e_2}"
    AZURE_OPENAI_MODEL_DALL_E_2 = "${azure_openai_model_dall_e_2}"
    TELEMETRY_PATH="${telemetrypath}"                        # [Optional]
    TEL_FLAG="${tel_flag}"                                   # [Optional]
    ```

    **NOTE:**
    ```sh
    To allow access to all sites, use the value "*" in "${allowed_origins}". Alternatively, you can specify a list of sites that should have access.
    ```
    ```sh
    AZURE_OPENAI_API_KEY_DALL_E_2 = "${azure_openai_api_key_dall_e_2}"
    AZURE_OPENAI_ENDPOINT_DALL_E_2 = "${azure_openai_endpoint_dall_e_2}"
    AZURE_OPENAI_API_VERSION_DALL_E_2 = "${azure_openai_api_version_dall_e_2}"
    AZURE_OPENAI_MODEL_DALL_E_2 = "${azure_openai_model_dall_e_2}"

    These values are required to generate images using the DALL·E 2 model via Azure OpenAI services.
    ```

3. Replace the placeholders with your actual values.

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

3. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running:`http://localhost:<portnumber?/rai/v1/llm/docs`

For API calls, please refer to the [API Document](responsible-ai-llm/docs/API_Doc.pdf)

## License

The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.

## Contact

If you have more questions or need further insights, feel free to Connect with us @ infosysraitoolkit@infosys.com
