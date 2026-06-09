# Responsible-AI-Moderation Layer 

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [Docker Image](#Docker-image)
- [License](#license)
- [Contact](#contact)
 
## Introduction
The **Moderation Layer** module provides model-based and template-based guardrails to moderate inputs by passing them through various checks like check for toxicity, profanity, prompt injection, jailbreak, privacy etc. The module also provides additional features like chain of thoughts, chain of verifications, token importance and LLM explanation.

This application is built using the Flask web framework.Leveraging the flexibility and scalability of Flask, this application provides some intuitve features as mentioned below.

## Features
1. **Model-based guardrail** : Here we use traditional AI models, libraries to test the input for various checks like prompt injection, jailbreak, toxicity etc.

2. **Template-based guardrail** : Here we  are making use of a Prompt Template for each evaluation check like prompt injection, jailbreak, etc. Prompt templates are a way to define reusable structures for prompting LLMs. It allows us to create a base prompt with placeholders that can be filled with different values to generate specific outputs. 

3. **Translate option** : Given that our model-based guardrails are optimized for English, we offer a translator option. In cases where prompts are in languages other than English, the translator converts them to English before passing them to the guardrails, thus providing extra protection against Multilingual Jailbreak attacks as well.

4. **Multimodal** : We are using multimodal functionality of GPT4o combined with our model based guardrail and template based guardrail to perform moderation checks like prompt injection, jailbreak etc. for text and image uploaded, respectively.

5. **Response comparision** : We are also providing response comparision between just LLM output and output from LLM with our guardrails. 

6. **Multiple LLM Support** : We have provided support to various LLM models to generate response and perform template based checks, these include : gpt-4o-mini, gpt-35-turbo, GPT-4-Turbo, Llama3-70b, anthropic.claude-3-sonnet, gemini-2.5.pro and gemini-2.5-flash models. You should have support of atleast one of these models.

## Prerequisites

1. Before installing the repo for Moderation Layer, first you need to install the repo for Moderation Models.
Please find the link for [Moderation Model](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/tree/main/responsible-ai-ModerationModel).
If you want to use template based guardrails then use [Admin Module](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/tree/master/responsible-ai-admin)

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



## Installation

### Steps for Installation :
**Step 1**  : Clone the repository `responsible-ai-moderationLayer`:
```sh
git clone <repository-url>
```

**Step 2**  : Navigate to the `responsible-ai-moderationLayer` directory:
```sh
cd responsible-ai-moderationLayer
```

**Step 3**  : Use the below link to download `en_core_web_lg` whl file -

[Download Link](https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl)
This will take 30-40 mins. 
Once done, put this inside `lib` folder of the repo `responsible-ai-moderationLayer`.


**Step 4**  : Activate the virtual environment for different OS.

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


**Step 5** : Go to the `requirements` directory where the `requirement.txt` file is present :

Now, install the requirements as shown below :
```sh
cd requirements
pip install -r requirement.txt
```

## Set Configuration Variables
After installing all the required packages, configure the environment variables necessary to run the APIs.

We are maintaining an environment file where we are keeping the Moderation Model urls,openai credentials,and many other attributes required for proper functioning of Moderation Layer.

1. Navigate to the `src` directory:
```sh
cd ..
```
2. Locate the file named as `.env`. This file contains key value pairs.There are some mandatory parameters and some are optional.

**Mandatory Parameters**
-------------------------------------------------------------------------------------------------------

1. **Passing Moderation Model URLs** : We have following env variables for passing Moderation Models:
```sh
SIMILARITYMODEL="${similaritymodel}" #[MANDATORY]
RESTRICTEDMODEL="${restrictedmodel}" #[MANDATORY]
DETOXIFYMODEL="${detoxifymodel}" #[MANDATORY]
PROMPTINJECTIONMODEL="${promptinjectionmodel}" #[MANDATORY]
JAILBREAKMODEL="${jailbreakmodel}" #[MANDATORY]
PRIVACY="${privacy}" #[MANDATORY]
SENTIMENT="${sentiment}" #[MANDATORY]
INVISIBLETEXT="${invisibletext}" #[MANDATORY]
GIBBERISH="${gibberish}" #[MANDATORY]
BANCODE="${bancode}" #[MANDATORY]

```
We need to pass the Model Urls in the same env file, which are nothing but apis for each Model that have been exposed in Moderation Model repo.

```sh
jailbreakmodel=<Put the model url needed for jailbreak>
restrictedmodel=<Put the model url needed for restricted topic>
detoxifymodel=<Put the model url needed for toxicity>
promptinjectionmodel=<Put the model url needed for prompt injection>
jailbreakmodel=<Put the model url needed for jailbreak>
privacy=<Put the model url needed for privacy>
sentiment=<Put the model url needed for sentiment>
invisibletext=<Put the model url needed for invisibletext>
gibberish=<Put the model url needed for gibberish>
bancode=<Put the model url needed for bancode>
```
For example :
```sh
jailbreakmodel="https://loremipsum.io/generator"
JAILBREAKMODEL="${jailbreakmodel}" 
```

2. **Passing LLM Credentials** : Each LLM model is optional

**GPT Credentials** : (Optional)

For this, you need to have Azure OpenaAI service. For more details, you can refer [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) for Pricing Details.

**AWS Credentials** : (Optional)

To use Claude foundation model via AWS Bedrock, you'll need:
1. An AWS account with Bedrock access
2. IAM permissions to invoke Bedrock models

For more information you can refer to
[Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
[AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

**LLAMA** : (Optional)

We have hosted the LLaMA 3-70B model on our own infrastructure. 
You can interact with it by hosting your model on your own infrastructure.
[LLaMA 3 Model Card (HuggingFace)](https://huggingface.co/meta-llama/Meta-Llama-3-70B)

**Gemini** : (Optional)

For the Gemini 2.5 Flash and Gemini 2.5 Pro models, we're using Google Generative AI SDK (google.generativeai). This only requires:
1. The model name (e.g., "gemini-2.5-pro")
2. Your Google API Key
[Gemini API Quickstart (Python)](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
[Google Generative AI Models List](https://ai.google.dev/gemini-api/docs/models)

Here we are passing LLM creds in the env file as follows. You should have atleast one model deployment endpoint or key. Like if you have support for gemini-2.5-pro model then other model fields are optional and only gemini-2.5-pro model will be mandatory in that case.

For gpt4o-mini : (Optional)
```sh
apibase_gpt4=<Enter the Azure OpenAI endpoint for gpt4o-mini, your endpoint should look like the following  https://YOUR_RESOURCE_NAME.openai.azure.com> #[OPTIONAL]
apiversion_gpt4=<Enter the Azure OpenAI version for gpt4o-mini> #[OPTIONAL]
openaimodel_gpt4=<Enter the Model name for gpt4o-mini> #[OPTIONAL]
apikey_gpt4=<Enter the Azure OpenAI API key for gpt4o-mini> #[OPTIONAL]
```
For gpt3.5 Turbo : (Optional)
```sh
apibase_gpt3=<Enter the Azure OpenAI endpoint for gpt3.5 Turbo> #[OPTIONAL]
apiversion_gpt3=<Enter the Azure OpenAI version for gpt3.5 Turbo> #[OPTIONAL]
openaimodel_gpt3=<Enter the Model name for gpt3.5 Turbo> #[OPTIONAL]
apikey_gpt3=<Enter the Azure OpenAI API key for gpt3.5 Turbo> #[OPTIONAL]
```
For gpt4O for multimodal functionality: (Optional)
```sh
api_base=<Enter the Azure OpenAI endpoint for gpt4o-mini> #[OPTIONAL]
api_key=<Enter the Azure OpenAI API key for gpt4o-mini> #[OPTIONAL]
api_version=<Enter the Azure OpenAI version for gpt4o-min> #[OPTIONAL]
model=<Enter the Model name for gpt4o-mini> #[OPTIONAL]
```

For llama3-70b : (Optional)
```sh
llamaendpoint3_70b=<Enter the endpoint where you have hosted the llama model> #[OPTIONAL]
aicloud_model_auth=<Give the endpoint to generate the authorization token> #[OPTIONAL]
```

For aws-anthropic bedrock model : (Optional)
```sh
awsservicename=<Enter the AWS service name> #[OPTIONAL]
awsmodelid=<Enter the AWS model id you are using> #[OPTIONAL]
accept=<You can give application/json> #[OPTIONAL]
contentType=<You can give application/json> #[OPTIONAL]
region_name=<Enter the region name for your service> #[OPTIONAL]
anthropicversion=<Enter the AWS model version > #[OPTIONAL]
AWS_KEY_ADMIN_PATH= <Enter the endpoint to generate the auth token to access the model> #[OPTIONAL]
```

For gemini-2.5-pro model : (Optional)
```sh
gemini_pro_model_name=<Enter the complete gemini model name here > #[OPTIONAL]
gemini_pro_api_key=<Enter the API key> #[OPTIONAL]
```

For gemini-2.5-flash model : (Optional)
```sh
gemini_flash_model_name=<Enter the complete gemini model name here > #[OPTIONAL]
gemini_flash_api_key=<Enter the API key> #[OPTIONAL]
```

Using the above values here :
```sh
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
LLAMA_ENDPOINT3_70b = "${llamaendpoint3_70b}" 
AICLOUD_MODEL_AUTH = "${aicloud_model_auth}"
AWS_SERVICE_NAME = "${awsservicename}"
AWS_MODEL_ID = "${awsmodelid}"
ACCEPT = "${accept}"
CONTENTTYPE = "${contentType}"
REGION_NAME = "${region_name}"
ANTHROPIC_VERSION = "${anthropicversion}" 
GEMINI_PRO_MODEL_NAME = "${gemini_pro_model_name}" 
GEMINI_PRO_API_KEY = "${gemini_pro_api_key}" 
GEMINI_FLASH_MODEL_NAME = "${gemini_flash_model_name}" 
GEMINI_FLASH_API_KEY = "${gemini_flash_api_key}" 
```

3. **Passing DB Related details** : Here we need to pass config details related to DB.
```sh
dbtype=<Mention as 'mongo' for Mongodb or 'psql' for Postgresql> #[OPTIONAL]
APP_MONGO_HOST=<Hostname for MongoDB or PostgreSQL> #[OPTIONAL]
username=<Enter the username for Database> #[OPTIONAL] 
password=<Enter the password for Database> #[OPTIONAL]
APP_MONGO_DBNAME=<Enter Database name for Mongo/Postgresql> #[OPTIONAL]

APP_MONGO_DBNAME="${APP_MONGO_DBNAME}" #If you are using DB then this will be mandatory and mention the dbname
DBTYPE="${dbtype}" #[MANDATORY]It will be mandatory if you will be using DB(values supported are mongo, psql , cosmos)

#If you are giving the DB type as psql or mongo then you need to define the username. password and mongohost
APP_MONGO_HOST="${APP_MONGO_HOST}" 
DB_USERNAME="${username}"
DB_PWD="${password}"

# If you are using Mongo DB then you need to define the mongo path
MONGO_PATH="mongodb://${DB_USERNAME}:${DB_PWD}@${APP_MONGO_HOST}/" #[OPTIONAL]
```

4. **Passing Cache details** : Pass the details for caching mechanism.

**Note :**  No. of cache entries depends upon no. of time the cache is invoked.
As per our design, when a single prompt is given , cache is invoked 15 times.
So, if you want to store entries :

for 10 user prompts ----> set cache_size as 150

for 20 user prompts ----> set cache_size as 300
```sh
cache_ttl=<Time for which entries will be stored in cache, mention in seconds>
cache_size=<Total entries in cache>
cache_flag=<cache enablement flag , set it to True if caching to be applied,otherwise False>

CACHE_TTL="${cache_ttl}" #[MANDATORY]
CACHE_SIZE="${cache_size}" #[MANDATORY]
CACHE_FLAG="${cache_flag}" #[MANDATORY]
```

5. **Setting Port No** : This will help to dynamically configure port no. for the Moderation layer Application.

As we know that this app is based on Flask, so you may give port no. as `5000` (Flask's default Port No), or any port no of your choice to make the app run.

Below are the entries for the same :
```sh
ports=< Set your port no. here>
PORT="${ports}" #[MANDATORY]
```

6. **Telemetry Related Details** : If you are setting up this application in your local, then mention as follows :
```sh 
TELEMETRY_ENVIRONMENT="${telemetryenviron}" #[MANDATORY]
telemetryenviron=<set it as "AZURE">
```
```sh
TEL_FLAG="${tel_flag}" #[MANDATORY]
tel_flag=<set it as False>
```
otherwise : If you are going to setup elasticsearch, kibana telemetry in your system, use the below configurations.
telemetrypath -> moderation telemetry path URL
coupledtelemetrypath --> coupled moderation telemetry path URL
adminTemplatepath --> admin telemetry path URL 
evalllmtelemetrypath --> eval telemetry path URL
```sh
tel_flag=<set it as True> 
TELEMETRY_PATH="http://<host:PORT>/path/v1/telemtry/<moderation telemetry api url>" 
COUPLEDTELEMETRYPATH="http://<host:PORT>/path/v1/telemtry/<coupled moderation telemetry api url>"
ADMINTEMPLATEPATH="http://<host:PORT>/path/v1/telemtry/<admin telemetry api url>"
EVALLLMTELEMETRYPATH="http://<host:PORT>/path/v1/telemtry/<eval moderation telemetry api url>"
```

7. **Target Environment** : Set the TARGETENVIRONMENT as azure 
```sh
TARGETENVIRONMENT="${environmentname}" #[MANDATORY]
environmentname=<set it as azure>
```

**Optional Parameters**
-------------------------------------------------------------------------------------------------------

1. **Setting Azure AI Tranlator API details** : Below is needed if you want to use Azure translate API for translating the user prompt.For this, you need to have Azure AI Translator service. For more details, you can refer [Azure AI Translator Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/translator/#resources) for Pricing Details.

Set azure translate details as follows :
```sh
AZURE_TRANSLATE_KEY = "${azuretranslatekey}" #[OPTIONAL]
AZURE_TRANSLATE_ENDPOINT = "${azuretranslateendpoint}" #[OPTIONAL]
AZURE_TRANSLATE_REGION = "${azuretranslateregion}" #[OPTIONAL]
azuretranslatekey=<Enter Azure Translate Key>
azuretranslateendpoint=<Enter Azure Translate Endpoint>
azuretranslateregion=<Enter the Region for Azure Translate>
```

2. **BLOOM and LLama Credentials** : Mention the endpoints for Bloom or Llama models.
```sh
BLOOM_ENDPOINT="${bloomendpoint}" #[OPTIONAL]
LLAMA_ENDPOINT="${llamaendpoint}" #[OPTIONAL]
bloomendpoint=<Mention Bloom endpoint>
llamaendpoint=<Mention Llama endpoint>
```

3. **Setting Details for OAuth2 authentication**: This is required to generate Bearer Token(for OAuth2), which is optional.
```sh
TENANT_ID = "${tenant_id}" #[OPTIONAL]
CLIENT_ID = "${client_id}" #[OPTIONAL]
CLIENT_SECRET = "${client_secret}" #[OPTIONAL]
AUTH_URL = "${auth_url}" #[OPTIONAL]
auth_url=<Mention Authenticaion url for token generation>
client_secret=<Client Secret key for token generation>
client_id=<Client Id for token generation>
tenant_id=<Tenant Id for token generation>
```

`SCOPE` is optional, this will be required only if we are using Microsoft or Google's support for token generation.
```sh
SCOPE = "${scope}" #[OPTIONAL]
scope=<Set the scope for Service Providers> 
```

4. **EXE creation** : This is required for exe creation of application. Set the following variables as follows :
```sh
exe_creation = <Set it to True or False based on user choice> #[OPTIONAL]
EXE_CREATION = "${exe_creation}" 
```

5. **Setting Vault** : This is required for setting up vault.

For local setup :
```sh
ISVAULT="${isvault}" #[OPTIONAL]
isvault=<set it as False> 
```
Otherise :
```sh
isvault=<set it as True>
```

6. **Health Check for Application** : This config detail will be required for health check of our application. It's typically used by external monitoring tools or systems to verify if your application is up and running correctly. When a monitoring tool sends a request to `/health` api in `router.py` file, the application responds with a status as `Health check Success` indicating that the application is healthy.

To perform health check , we need to set the following flag :

For local setup :
```sh
log=<set it to false>
```
Otherwise :
```sh
log=<set it to true> 
LOGCHECK="${log}" #[OPTIONAL]
```

7. **SSL Verify** : If you want to by pass verify SSL check then set the variable value to False otherwise True:

```sh
verify_ssl=<set it to True or False as required> 
VERIFY_SSL="${verify_ssl}" #[OPTIONAL]
```

8. Rest all environment variables not mentioned above but are mentioned in `.env` file are completely optional and need not to be set.


## Running the Application

**Note** : Please don't run the api for feedback i.e. `/rai/vi/moderations/feedback` as this endpoint will be deprecated from the next release onwards.

Once we have completed all the above mentioned steps, we can start the service.

1. Navigate to the `src` directory:

2. Run `main.py` file:
    ```sh
    python main.py
     ```

3. PORT_NO : Use the Port No that is configured in `.env` file.

   Open the following URL in your browser:

   `http://localhost:<PORT_NO>/rai/v1/moderations/docs`

4. **For PII Entity Detection and Blocking :**
For `rai/vi/moderations` and `rai/vi/moderations/coupledmoderations` APIs , we have configured parameters to be blocked under `PiientitiesConfiguredToBlock` coming in `ModerationCheckThresholds` in the Request Payload.

These parameters are configurable. For instance, I have provided here some list of entities to block
```sh
"AADHAR_NUMBER" : to block Aadhar Number (Aadhar number should not have spaces in between)
"PAN_Number" : to block PAN Card Number
"IN_AADHAAR" : to block Indian Aadhar number ( this is added due to updated presidio analyzer, which has wide set of entities to detect, make sure Indian Aadhar number should not have spaces in between)
```
```sh
"IN_PAN" : to block Indian PAN Card number ( this is added due to updated presidio analyzer, which has wide set of entities to detect)
```
```sh
"US_PASSPORT" : to block US Passport Number
"US_SSN" : to block US SSN Number
```
which can be added as below :
```sh
"ModerationCheckThresholds": {
    "PiientitiesConfiguredToBlock": [
      "AADHAR_NUMBER",
      "PAN_Number",
      "IN_PAN",
      "IN_AADHAAR",
      "US_PASSPORT",
      "US_SSN"
    ]
}
```

5. **Using Bearer Token for OAuth2 for coupledModeration**
- You need to use the OAuth2 Authentication Token provided Azure or GCP Platform ( Please refer step 3 under **Optional Parameters** in section `Set Configuration Variables` on how to generate OAuth2 token)
- Use that token in 2 places :
  
     a) `Authorize` at the top of the Swagger UI : On clicking on it, you will get an option as **BearerAuth  (http, Bearer)** and then **Value**, in the empty text box , just pass the token and click on `Authorize` and then `Close`.

     b) For Coupled Moderation API : On expanding it, you will get an option as `Parameters`. There, you will find a text box beside `autorization`. Mention the token in below format :
  ```sh
  Bearer <token>
  ```

6. **For the api /rai/v1/moderations/getTemplates/{userid}**
   - For this , first you need to clone the admin repository. Link mentioned :  [Admin Repo](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/tree/main/responsible-ai-admin)
   - Once done, please do the necessary steps to run the admin repo codebase in your local (as mentioned in admin readme file)
   - Go to the API ```api/v1/rai/admin/createCustomeTemplate``` and provide the necessary details to create custom template. The payload is like this :
  
     For Text Based Templates :
     ```sh
         {
           "userId": "123",
           "mode": "Master_Template/Private_Template", -> Master templates accessible to all, Private templates only to particular user with userid
           "category": "SingleModel",
           "templateName": "Template1",   <------> Name of the Prompt Template
           "description": "Template1",  <-----> Short description on what the template is about
           "subTemplates": [
             {
               "subtemplate": "evaluation_criteria",
               "templateData": ""
             },
             {
               "subtemplate": "prompting_instructions",
               "templateData": ""
             },
             {
               "subtemplate": "few_shot_examples",
               "templateData": ""
             }
           ]
         }
     ```

     For Image based Templates :
     ```sh
         {
           "userId": "123",
           "mode": "Master_Template/Private_Template", -> Master templates accessible to all, Private templates only to particular user with userid
           "category": "MultiModel",
           "templateName": "Template1",   <------> Name of the Prompt Template
           "description": "Template1",  <-----> Short description on what the template is about
           "subTemplates": [
             {
               "subtemplate": "evaluation_criteria",
               "templateData": ""
             },
             {
               "subtemplate": "prompting_instructions",
               "templateData": ""
             },
             {
               "subtemplate": "few_shot_examples",
               "templateData": ""
             }
           ]
         }
     ```

     - Once the above thing is done, in the `.env` file, mention the admin api running in local for the field as shown below :
       ```sh
       adminTemplatepath = "<admin_api_url>" `[ Ex : http://localhost:8019//api/v1/rai/admin/getCustomeTemplate/"]`
       ADMINTEMPLATEPATH="${adminTemplatepath}"
       ```
     - Post this, you can run the api ```api/v1/rai/admin/createCustomeTemplate``` and as success response, you will get response like this :
       ```sh
        Templates Retrieved
       ```

7. **For Template-based Checks**
   - There are 2 APIs exposed that make use of prompt templates to evaluate adversarials from text( text moderation) or image(image moderation).
   - Some Master Templates we are using for the api `/rai/v1/moderations/evalllm` :
     ```sh
     1. Prompt Injection Check : to check for prompt injection
     2. Jailbreak Check : to check for Jailbreak checks
     3. Fairness and Bias Check: to check for biasness
     4. Privacy Check : to check for Privacy
     5. Language Critique Coherence Check : through this check, LLM will evaluate the quality of the provided text, focusing on the coherence aspect.
     6. Language Critique Fluency Check : through this check, LLM will evaluate the quality of the provided text, focusing on the fluency aspect.
     7. Language Critique Grammar Check : through this check, LLM will evaluate the quality of the provided text, focusing on the grammar aspect.
     8. Language Critique Politeness Check : through this check, LLM will evaluate the quality of the provided text, focusing on the politeness aspect.
     9. Response Completness Check : to check if the LLM response is complete w.r.t the user prompt
     10. Response Conciseness Check : to check if the LLM response is concise and brief w.r.t. the user prompt 
     11. Response Language Critique Coherence Check : through this check, LLM will evaluate the quality of the LLM Response, focusing on the coherence aspect.
     12. Response Language Critique Fluency Check : through this check, LLM will evaluate the quality of the LLM Response, focusing on the fluency aspect.
     13. Response Language Critique Grammar Check : through this check, LLM will evaluate the quality of the LLM Response, focusing on the grammar aspect.
     14. Response Language Critique Politeness Check : through this check, LLM will evaluate the quality of the LLM Response, focusing on the politeness aspect.
     ```
         
   - Some Master Templates we are using for the api `/rai/v1/moderations/multimodal` :
     ```sh
     1. Image Restricted Topic Check : to restrict certain topics like "terrorrism" , "explosives"
     2. Image Prompt Injection Check : to check for Prompt Injection
     3. Image Jailbreak Check : to check for Jailbreak attacks
     4. Image Toxicity Check : to check for Toxicity
     5. Image Profanity Check : to check for Profanity
     ```

     We need to use these template names in our request payload as shown below :
     ```sh
     {
      "AccountName": "None",
      "PortfolioName": "None",
      "userid": "None",
      "lotNumber": 1,
      "Prompt": "Which is the biggest country in the world?",
      "model_name": "gpt4",
      "temperature": "0",
      "PromptTemplate": "GoalPriority",
      "template_name": "PROMPT_INJECTION"  <---------->   template name as mentioned above
     }
     ```

     **Note :** Change model_name in payload according to the model which you want to use:
     gpt4 for GPT4o-mini or GPT4-Turbo model
     gpt3 for GPT35-Turbo model
     Llama3-70b for Llama3-70b model
     AWS_CLAUDE_V3_5 for AWS Bedrock Claude model
     Gemini-Pro for Gemini 2.5 Pro model
     Gemini-Flash for Gemini 2.5 Flash model

## Docker Image
The Docker image for the Moderationlayer module has been published on Docker Hub. You can access it here: [ModerationLayer image](https://hub.docker.com/repository/docker/infosysresponsibleaitoolkit/responsible-ai-moderationlayer)
  
## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.txt](LICENSE.txt) file.

## Contact
If you have more questions or need further insights please feel free to connect with us at
DL : Infosys Responsible AI
Mailid: Infosysraitoolkit@infosys.com
