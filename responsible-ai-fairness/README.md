# Responsible-AI-Fairness

## Table of contents
- [Responsible-AI-Fairness](#responsible-ai-fairness)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configurations](#configurations)
      - [Database Configurations](#database-configurations)
      - [Header Configurations](#header-configurations)
      - [Blob Containers and API Configurations](#blob-containers-and-api-configurations)
  - [Features](#features)
  - [License](#license)
  - [Open Source Tools used](#open-source-tools-used)
  - [Changelog](#changelog)
    - [Bug Fixes](#bug-fixes)
    - [Changes:](#changes)
  - [Limitations](#limitations)
  - [Telemetry](#telemetry)
  - [Roadmap](#roadmap)
  - [Building and Distributing the Python Package as a Wheel (WHL) File](#building-and-distributing-the-python-package-as-a-wheel-whl-file)

## Introduction
Responsible-ai-fairness offers solutions for Traditional AI and LLM's fairness and bias evaluations. For traditional classification problems, the training datasets and model's predictions can be analyzed and mitigated for Group Fairness. Individual Fairness analysis is also supported to get a comprehensive analysis. For Large Language Models, given text is evaluated for bias context and highlights the affected groups and bias types using GPT-4.

## Requirements
1. Python >= 3.11
2. pip
3. Mongo DB
4. VSCode
5. infosys_responsible_ai_fairness-1.1.5-py2.py3-none-any.whl file having code to calculate metrics scores for bias analysis using [aif360](https://aif360.readthedocs.io/en/stable/), [Holistic AI](https://github.com/holistic-ai/holisticai), [Fairlearn](https://github.com/fairlearn/fairlearn)
6. BART-large-mnli is a variant of the BART model specifically fine-tuned for multi-label natural language inference (MNLI) tasks. It features 406 million parameters, a maximum token size of 1024, 24 transformer layers, and a hidden size of 1024.  
Steps to Download BART-large-mnli:
   1.	Identify the Model URL: Navigate to the BART model page on the Hugging Face Model Hub. For example, for facebook/bart-large, the URL is:
      https://huggingface.co/facebook/bart-large-mnli
   2.	Find the Model Files: On the model page, you can see the available model files and can directly download from the huggingface.
      
       •	pytorch_model.bin (the model weights)
      	
       •	config.json (model configuration)
 
       •	tokenizer.json or other tokenizer file.

       •	tokenizer_config.json .

       •	vocab.json.

       •	merges.txt.

       •	model.safetensors

   3.	or alternatively, you can download the Files using curl or wget to download the files directly from the command line.
     	
       curl -L -o pytorch_model.bin https://huggingface.co/facebook/bart-large/resolve/main/pytorch_model.bin
 
       curl -L -o config.json https://huggingface.co/facebook/bart-large/resolve/main/config.json
 
       curl -L -o tokenizer.json https://huggingface.co/facebook/bart-large/resolve/main/tokenizer.json

       curl -L -o tokenizer_config.json https://huggingface.co/facebook/bart-large/resolve/main/tokenizer_config.json

       curl -L -o merges.txt https://huggingface.co/facebook/bart-large/resolve/main/merges.txt

       curl -L -o model.safetensors https://huggingface.co/facebook/bart-large/resolve/main/model.safetensors

       curl -L -o vocab.json https://huggingface.co/facebook/bart-large/resolve/main/vocab.json
   
   4. once all the files are downloaded, move them to **responsible-ai-fairness/responsible-ai-fairness/models**



## Installation
1.	Clone the repository
2.	Create a virtual environment using the command 
```bash
python -m venv .venv
```
and activate it by going to
```bash
.venv\Scripts\activate
```
3.	Setup the DB
      1. Create database in mongodb and add the db name in .env file
4.	Install dependencies. 
      1. Go to **responsible-ai-fairness\responsible-ai-fairness\requirements** and run following commands 
      ```bash 
         pip install -r requirements.txt.
      ```
      2. if you are on windows, please add **../** in front to .whl file in requirements.txt to install without any errors.
5. Add required configurations provided below in .env file.
6. Run the application using below steps:
      1. Go to responsible-ai-fairness/responsible-ai-fairness/src 
      2. Run 
      ```bash 
         python main_api.py 
      ```
7. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running: `http://localhost:8000/api/v1/fairness/docs#/`
   
## Configurations
 1. Add required environment variables.
 2. Below are the list of env one needs to add, to run the application, add required ones only and for the rest one can keep it as it is. .env template is there in the src folder.

#### Database Configurations
| Key         | Placeholder Value | sample Value     | Required |
|-------------|-------------------|------------------|----------|
| DB_NAME     | "${dbname}"       | "rai_repository"   |  yes     |
| DB_NAME_WB  | "${dbname_wb}"    | "rai_repository"   |  yes     |
| DB_USERNAME | "${username}"     | "user"           |  optional|
| DB_PWD      | "${password}"     |                  |  optional|
| DB_IP       | "${ipaddress}"    |                  |  optional|
| DB_PORT     | "${port}"         |                  | optional |
| MONGO_PATH  | "mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/" | "mongodb://localhost:27017/" | yes |
| COSMOS_PATH | "${cosmos_path}"  |      | optional |
| DB_TYPE     | "${dbtype}"       | "mongo"          | yes |


#### Header Configurations
| Key                     | Placeholder Value       | Sample Value     |Required |
|-------------------------|-------------------------|------------------|----------|
| allow_methods           | "${allow_methods}"      |       '["GET", "POST"]'           | Optional |
| allow_origin            | "${allow_origin}"       |       ["*"]            | optional |
| content_security_policy | "${content_security_policy}"|  "default-src 'self'; img-src data: https:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"    | optional |
| cache_control           | "${cache_control}"      |      no-cache; no-store; must-revalidate            | Optional |
| XSS_header              | "${xss_header}"         |    1; mode=block               | Optional |
| Vary_header             | "${vary_header}"        |         Origin         | Optional |
| X-Frame-Options         | "${X-Frame-Options}"    |            SAMEORIGIN       | Optional |
| X-Content-Type-Options  | "${X-Content-Type-Options}" |     nosniff         | Optional |
| Pragma                  | "${Pragma}"             |     no-cache             | Optional |


#### Blob Containers and API Configurations

| Key                                | Placeholder Value                     | Sample Value     | Required |
|------------------------------------|---------------------------------------|------------------|----------|
| Dt_containerName                   | "${dt_containerName}"                 |                  | Optional |
| Model_CONTAINER_NAME               | "${model_containerName}"              |                  | Optional |
| HTML_CONTAINER_NAME                | "${html_containerName}"               |                  | Optional |
| PDF_CONTAINER_NAME                | "${rai-pdf-reports}"               |                  | Optional |
| CSV_CONTAINER_NAME                | "${rai-datasets}"               |                  | Optional |
| ZIP_CONTAINER_NAME                | "${rai-zip-files}"               |                  | Optional |
| AZURE_UPLOAD_API                   | "${azure_upload_api}"                 |                  | Optional |
| AZURE_GET_API                      | "${azure_get_api}"                    |                  | Optional |
| GCP_UPLOAD_API                     | "${gcp_upload_api}"                   |                  | Optional |
| GCP_GET_API                        | "${gcp_get_api}"                      |                  | Optional |
| AWS_UPLOAD_API                     | "${aws_upload_api}"                   |                  | Optional |
| AWS_GET_API                        | "${aws_get_api}"                      |                  | Optional |
| tel_Falg                           | "${tel_Falg}"                         |                  | Optional |
| MIXTRAL_URL                        | "${mixtral_url}"                      |                  | Optional |
| MIXTRAL_ACCESS_TOKEN               | "${mixtral_access_token}"             |                  | Optional |
| FAIRNESS_TELEMETRY_URL             | "${fairness_telemetry_url}"           |                  | Optional |
| REPORT_URL                         | "${reporturl}"                        |                  | Optional |
| GEMINI_API_KEY                     | "${gemini_api_key}"                   |  gemini_key      | Yes |
| GEMINI_FLASH_MODEL_NAME            | "${gemini_flash_model_name}"          |  gemini_flash_model_name  | Yes |
GEMINI_PRO_MODEL_NAME                | "${gemini_pro_model_name}"            |  gemini_pro_model_name               | Yes 
| OPENAI_API_KEY                     | "${openai_api_key}"                   |      open_ai_key            | Yes |
| OPENAI_API_BASE                    | "${openai_api_base}"                  |      open_ai_base/endpoint            | Yes |
| OPENAI_API_TYPE                    | "${openai_api_type}"                  |      open_ai_type            | Yes |
| OPENAI_API_VERSION                 | "${openai_api_version}"               |      open_ai_version            | Yes |
| OPENAI_ENGINE_NAME                 | "${openai_engine_name}"               |      open_ai_engine_name           | Yes |
| ACTIVE_LLM | "${active_llm}" | Options: azureopenai, gemini-2.5-flash, gemini-2.5-pro, aws | Yes |
| AUTH_TYPE                          | "${authtype}"                         | "none"           | Yes      |
| SECRET_KEY                         | "${secretkey}"                        |                  | Optional |
| AZURE_CLIENT_ID                    | "${azureclientid}"                    |                  | Optional |
| AZURE_TENANT_ID                    | "${azuretenantid}"                    |                  | Optional |
| AZURE_AD_JWKS_URL                  | "${azuread_jwks_url}"                 |                  | Optional |
| Analyse_url                        | "${analyse_url}"                      |                  | Optional |
| Mitigate_url                       | "${mitigate_url}"                     |                  | Optional |
| Analyse_dowl_url                   | "${analyse_dowl_url}"                 |                  | Optional |
| AWS_SERVICE_NAME | "${awsservicename}" | | Yes |
|AWS_KEY_ADMIN_PATH | "${awsadminpath}"| | Yes |
|AWS_MODEL_ID | "${awsmodelid}"| | Yes |
|REGION_NAME | "${region_name}" | | Yes |
|ACCEPT | "${accept}" | | Yes |
|CONTENTTYPE | "${contentType}" ||  Yes |
|ANTHROPIC_VERSION | "${anthropicversion}" | | Yes |
| VERIFY_SSL | "${verify_ssl}" | Options: True, False | Yes |

## Features
For more details refer our [API Documentation](responsible-ai-fairness\docs\FAIRNESS_API_DOCUMENTATION.pdf)

| Model Type                      | Phase         | Function  | Description                                                                 |
|---------------------------------|---------------|-----------|-----------------------------------------------------------------------------|
| Traditional Binary classification | Pretrain      | Analyze   | Analyze for bias in structured dataset based on ground truth                |
| Traditional Binary classification | Posttrain     | Analyze   | Analyze for bias in structured dataset based on model's predictions         |
| Traditional Binary classification | Pretrain      | Mitigation | Mitigate the bias in the pretrain dataset                                   |
| Traditional Binary classification | Individual Metric | Analyze   | Analyze for bias in structured dataset based on individuals in the dataset   |
| Large Language Model            | NA            | Analyze   | Analyze bias in given unstructured text and images using Open AI GPT model, Gemini 2.5 flash model, Gemini 2.5 pro model and AWS claud anthropic model.(For this please add required credentials in env)|

## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.

## Open Source Tools used
| Open Source Tools Used | Link |
|------------------------|------|
| IBM AiF360             | https://github.com/Trusted-AI/AIF360 |
| Holistic AI            | https://github.com/holistic-ai/holisticai |
| Microsoft Fairlearn    | https://github.com/fairlearn/fairlearn |
| Facebook BART model    | https://huggingface.co/facebook/bart-large-mnli |

## Changelog
1. Introduced ACTIVE_LLM Environment Variable:
    A new environment variable ACTIVE_LLM has been added to define the default Large Language Model (LLM) used for bias analysis when the evaluator parameter is not provided by the user.

    This applies to the following endpoints:
        Bias analysis in Text
        Bias analysis in Image

    This variable is also used to determine the LLM for bias evaluation in structured text scenarios.

    Supported Values for ACTIVE_LLM:
        The following values can now be set for the ACTIVE_LLM environment variable (refer to the Configurations section for usage):

            azureopenai
            gemini_2.5_flash
            gemini_2.5_pro
            aws

2. Evaluator Parameter Made Optional:
    The evaluator parameter is now optional for the Bias analysis in Text and Bias analysis in Image endpoints.If omitted, the value from ACTIVE_LLM will be used instead, enabling more flexible configuration between user request scope (evaluator) and application scope (ACTIVE_LLM).

    Added Support for New Evaluators:
        The following evaluator strings are now supported:
            GPT_4O
            GEMINI_2.5_FLASH
            GEMINI_2.5_PRO
            AWS_CLAUDE_V3_5


## Limitations
1. As of now analysing bias for classification models for traditional AI.
2. Data mitigation for preprocessing: 
   1. Reweighting can lead to overfitting on minority groups, potentially reducing overall model performance on the dataset.
   2. Adjusting weights can distort the original data distribution, leading to a loss of valuable information and potential misrepresentation of the data.
3. As of now mitigating bias for preprocessing dataset.
4. As of now, we are generating token from an endpoint which is not open-sourced.

## Telemetry
1. Make tel_Falg as True.
. Follow the steps given in `responsible-ai-telemetry` to setup telemetry.
3. Pass the enpoint `/rai/v1/telemetry/errorloggingtelemetryapi` from above setup swagger ui to the varaible 'FAIRNESS_TELEMETRY_URL' in .env

## Roadmap
1. Unstructured text training data validation for Bias.
2. REST call support for text validationt to support ollama or similar model hosting.

## Building and Distributing the Python Package as a Wheel (WHL) File

This section outlines the steps to create a distributable Wheel (WHL) file for the `infosys_responsible_ai_python_package` and integrate it into the `responsible_ai_fairness/lib` directory.

**Steps:**

1.  **Install `wheel` and `setuptools`:**
    ```bash
    pip install wheel setuptools
    ```
2.  **Navigate to the Package Directory:**
    ```bash
    cd infosys_responsible_ai_python_package
    ```
3.  **Build the Wheel File:**
    ```bash
    python setup.py bdist_wheel --universal
    ```
4.  **Locate and Copy the Wheel File:**
    Navigate to `dist` and copy the `.whl` file.
5.  **Paste the Wheel File into the `lib` Directory:**
    Navigate to `responsible_ai_fairness/lib` and paste.
6.  **Update `requirements.txt`:**
    Replace the package entry with the `.whl` filename.

**Note:**
* Ensure `setup.py` version is correct.
* `--universal` is optional.
* Update `requirements.txt` with the `.whl` filename.
