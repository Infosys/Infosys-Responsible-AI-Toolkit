# responsible-ai-trustllm

## Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Features](#features)
- [Installation](#installation)
- [Open Source Tools used](#open-source-tools-used)
- [Configurations](#configurations)
- [API Endpoints](#api-endpoints)
- [License](#license)

## Introduction
 [TrustLLM](https://github.com/HowieHwong/TrustLLM) is a tool used to benchmark text generating LLMs. Privacy, Fairness, Safety, Truthfulness, Ethics of the LLM are evaluated using the dataset provided. We have created a wrapper around this tool to ease the benchmarking process.

## Requirements
1. Python >= 3.11
2. pip
3. Mongo DB
4. VSCode


## Features
- Benchmarking of huggingface models using the dataset provided.
- Adding, deleting, retriving scores from DB.

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
      1. Go to **responsible-ai-benchmarking\requirements** and run 
      ```bash 
         pip install -r requirement.txt
      ```
      2. if you are on windows, please add **../** in front to .whl file in requirements.txt to install without any errors.
5. Add required configurations provided below in .env file.
6. Run the application using below steps:
      1. Go to responsible-ai-benchmarking\src 
      2. Run 
      ```bash 
         python main_api.py 
      ```
7. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running:`http://localhost:8000/api/v1/trustllm/docs#/`

## Open Source Tools used
| Open Source Tools Used | Link |
|------------------------|------|
| TrustLLM             | https://github.com/HowieHwong/TrustLLM.git |

## Configurations
 1. Add required environment variables.
 2. Below are the list of env one needs to add, to run the application, add required ones only and for the rest one can keep it as it is. .env template is there in the src folder.

| Key         | Placeholder Value | sample Value     | Required |
|-------------|-------------------|------------------|----------|
| DB_NAME    | "${dbname}"      | "rai_repository"   |  yes     |
| DB_USERNAME  | "${username}"    |  "user"  |  yes   |
| DB_PWD | "${ipaddress}"     |            |  optional|
| DB_PORT      | "${port}"     |                  |  optional|
| MONGO_PATH       | "mongodb://localhost:/"    |   "mongodb://localhost:27017/ "              |  yes |
| COSMOS_PATH    | "${cosmos_path}"         |                  | optional |
| DB_TYPE | "${dbtype}" | "mongo" | yes |
| allow_methods | "${allow_methods}"  | '["GET", "POST"]'  | yes |
| allow_origin     | "${allow_origin}"       | ["*"]         | yes |
| content_security_policy | "${content_security_policy}" | "default-src 'self'; img-src data: https:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" | yes |
| cache_control | "${cache_control}" | "private, no-store" | yes |
| XSS_header | "${xss_header}" | "1; mode=block" | yes |
| Vary_header | "${vary_header}" | 'Origin' | yes |
| azure_engine | "${azure_engine}" | Azure Engine Name | yes |
| azure_api_base | "${azure_api_base}" | Azure API Base | yes |
| openai_key | "${openai_key}" | OpenAI Key | yes |
| azure_api_version | "${azure_api_version}" | Azure API Version | yes |


##Note:
Offline Generation and evaluation required GPU to run. To install cuda, execute the following command <br>
``` bash 
   pip3 install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu121
```

## API Endpoints
# TrustLLM API Documentation

| Endpoint | Purpose | Key Features |
|----------|---------|--------------|
| `/api/v1/trustllm/dataset` | Generate evaluation datasets | - Create datasets for model assessment<br>- Focus areas include:<br>  * Privacy<br>  * Fairness<br>  * Safety<br>  * Truthfulness<br>  * Ethics |
| `/api/v1/trustllm/offline/generation/` | Generate responses from open-source models | - Use models from platforms like Hugging Face<br>- Benchmarking capabilities for:<br>  * Privacy<br>  * Fairness<br>  * Safety<br>  * Truthfulness<br>  * Ethics |
| `/api/v1/trustllm/online/generation/` | Generate responses from internal models | - Utilize internally hosted models<br>- Evaluation focus on:<br>  * Privacy<br>  * Fairness<br>  * Safety<br>  * Truthfulness<br>  * Ethics |
| `/api/v1/trustllm/evaluation` | Evaluate generated responses | - Assess responses from offline and online models<br>- Multiple evaluation metrics for:<br>  * Privacy<br>  * Fairness<br>  * Safety<br>  * Truthfulness<br>  * Ethics |
| `/api/v1/trustllm/scores/getScores` | Retrieve leaderboard scores | - Access performance metrics<br>- Compare and rank models<br>- View evaluation results |
| `/api/v1/trustllm/scores/addScore` | Add evaluation scores | - Update leaderboard database<br>- Track model performance<br>- Record new evaluation metrics |
| `/api/v1/trustllm/scores/deleteScore` | Remove leaderboard scores | - Delete outdated or incorrect scores<br>- Maintain accurate leaderboard<br>- Manage performance records |

## Additional Notes
- Each endpoint is designed to support comprehensive model evaluation
- Focuses on critical aspects of trustworthy AI development
- Provides a systematic approach to assessing model performance

## License
The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.
