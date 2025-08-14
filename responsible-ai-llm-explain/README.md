# Responsible-AI-LLM-Explain

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)

## Introduction

**LLM Explain** provides explanations for Large Language Models using methods such as token importance, Graph of Thoughts, Logic of Thought, Thread of Thought , Chain of Thought and Search Augmentation. It evaluates the responses with metrics including uncertainty, relevancy, and coherence to ensure the reliability and clarity of Generative AI models' outputs.

## Features
- **Sentiment Analysis**
    
    Sentiment analysis analyzes the sentiment of a given prompt, classifies the sentiment, and identifies the key keywords that significantly influenced the model's sentiment assignment. Additionally, it provides a detailed explanation of the decision-making process behind the sentiment classification.
- **Token Importance**

    Token importance in large language models identifies which words or parts of words in a prompt are crucial for shaping the model's response. It helps us understand which tokens significantly influence the output, providing insights into how the model interprets and generates its responses.

- **Graph of Thought**

    The Graph of Thoughts reasoning process in large language models is a way to visualize how the model thinks. Imagine the model's ideas as dots, and the connections between them as lines. This method creates a map of these dots and lines to show how the model connects different pieces of information to come up with its answers. It helps us understand the model's logical flow and ensures that its reasoning makes sense, like how a human would think through a problem step-by-step.

- **Search Augmentation**

    Search augmentation in large language models involves using internet searches to validate and enhance the model's responses. This process supplements the model's answers with additional information from online sources, improving accuracy and reliability by cross-checking and complementing the original output.

- **Explanation Metrics**

    LLM Explanation metrics involves assessing how well a large language model's response addresses a query. It focuses on evaluating the quality of the model's answers to ensure they are clear, accurate, and relevant. This process helps in understanding and validating the usefulness of the model's responses.

    - **Uncertainty**: Measures the model’s confidence in its responses, highlighting areas where the model may exhibit lower certainty.

    - **Coherence**: Assesses the logical consistency and organization of the explanation, ensuring a clear and structured line of reasoning.

- **Chain of Thought**

    It refers to a structured problem-solving approach that breaks down complex tasks into a series of logical, step-by-step processes. It allows the model to systematically explore each part of the problem, making the reasoning more transparent and improving the accuracy of the solution by focusing on each individual step before arriving at a final answer.

- **Thread of Thoughts**

    Thread of Thoughts addresses challenges in chaotic or complex contexts where large language models (LLMs) struggle to sift through and prioritize relevant information amidst an overwhelming amount of data. It helps organize and guide the model’s reasoning by maintaining a clear path of thought, ensuring that important details are identified and addressed without getting lost in extraneous information.

- **Chain of Verification**

    Chain of Verification is a mechanism implemented to directly counteract hallucinations, which occur when an LLM generates responses that are logically coherent but factually incorrect. This approach ensures that each piece of information or step in the model's reasoning process is validated or cross-checked, reducing the likelihood of errors or false conclusions by reinforcing the reliability of the generated output.

- **Chain of Thought for RAG**

    Chain of Thought for RAG (Retrieval-Augmented Generation) outlines the reasoning steps an LLM takes to generate a response, combining the input prompt with relevant context retrieved from external sources. The model explains how it integrates both the prompt and the additional information to form a coherent answer. In a RAG-based system, context is retrieved from vector storage and used to enrich the response. This approach ensures the model's response is grounded in relevant, factual data. It also provides transparency into the reasoning behind the response, clarifying which details were prioritized.

**Note:** 
- `Chain of Thought for RAG`This feature is available under **Moderation Layer** (responsible-ai-moderationLayer) repository.
Please follow the setup instructions in the README file of the moderation layer repository to configure them. Ensure that the service is up and running to execute.

- Currently not added Gemini support for `Graph of Thought`. Except GOT all features have Gemini Support.

- For `Bulk Processing` current version not supporting (Evaluation Metrices, Sentiment, Safesearch, All) methods.

## Installation
To run the application, first we need to install Python and the necessary packages:

1. Install Python (version 3.11.x) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.

2. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

3. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

4. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
         ```

5. Upgrade pip:
    ```sh
    python -m pip install --upgrade pip
    ```

6. Navigate to the `responsible-ai-llm-explain` directory:
    ```sh
    cd responsible-ai-llm-explain
    ```
    
7. Go to the `requirements` directory where the `requirement.txt` file is present and install the requirements:
    ```sh
    cd responsible-ai-llm-explain\requirements
    pip install -r requirement.txt
    ```
## Set Configuration Variables

After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `llm_explain` directory:
    ```sh
    cd ..
    cd src/llm_explain
    ```

2. Locate the `.env` file in the project directory. This file contains several configuration keys. Make sure to fill in the mandatory fields:

    ```sh
    AZURE_OPENAI_API_KEY = "${apikey}"          # [Mandatory]
    AZURE_OPENAI_API_VERSION = "${apiversion}"  # [Mandatory]
    AZURE_OPENAI_ENDPOINT = "${azureendpoint}"  # [Mandatory]
    AZURE_DEPLOYMENT_ENGINE = "${engine}"       # [Mandatory]
    SERPER_KEY = "${serperkey}"                 # [Mandatory]
    ALLOWED_ORIGINS = "${allowedorigins}"       # [Mandatory]
    PERPLEXITY_API_KEY = "${perplexity_api_key}" # [Mandatory]
    PERPLEXITY_MODEL = "${perplexity_model}"     # [Mandatory]
    PERPLEXITY_URL = "${perplexity_url}"         # [Mandatory]
    ERROR_LOG_TELEMETRY_URL = "${errorlogtelemetryurl}" # [Optional]
    TELEMETRY_FLAG = "${telemetryflag}"         # [Optional]
    LLAMA_ENDPOINT =  "${llamaendpoint}"        # [Optional]
    BULK_TELEMETRY_URL = "${bulk_telemetry_url}" #[Optional]
    GEMINI_MODEL_NAME_PRO ="${gemini_model_name_pro}" #[Optional]
    GEMINI_MODEL_NAME_FLASH = "${gemini_model_name_flash}" #[Optional]
    GEMINI_API_KEY = "${gemini_api_key}"         #[Optional]
    AWS_KEY_ADMIN_PATH = "${aws_key_admin_path}" #[Optional]
    ANTHROPIC_VERSION = "${anthropic_version}"   #[Optional]
    CONTENTTYPE = "${contenttype}"               #[Optional]
    ACCEPT = "${accept}"                         #[Optional]
    AWS_MODEL_ID  = "${aws_model_id}"            #[Optional]
    REGION_NAME= "${region_name}"                #[Optional]
    AWS_SERVICE_NAME = "${aws_service_name}"     #[Optional]
        ```
    ```sh
    ALLOWED_ORIGINS = "${allowed_origins}"     # ALLOWED_ORIGINS ="*"         
    To allow access to all sites, use the value *. Alternatively, you can specify a list of sites that should have access.
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

3. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running: `http://localhost:8002/rai/v1/llm-explainability/docs`

For API calls, please refer to the [API Document](responsible-ai-llm-explain/docs/API_Doc.pdf)


## Referred Citations
```
@misc{besta2023got,
  title = {{Graph of Thoughts: Solving Elaborate Problems with Large Language Models}},
  author = {Besta, Maciej and Blach, Nils and Kubicek, Ales and Gerstenberger, Robert and Gianinazzi, Lukas and Gajda, Joanna and Lehmann, Tomasz and Podstawski, Micha{\l} and Niewiadomski, Hubert and Nyczyk, Piotr and Hoefler, Torsten},
  year = 2023,
  eprinttype = {arXiv},
  eprint = {2308.09687}
}

```

## License

The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.

## Contact

If you have more questions or need further insights, feel free to Connect with us @ infosysraitoolkit@infosys.com


