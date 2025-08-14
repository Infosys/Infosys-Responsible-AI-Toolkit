# Responsible-AI-Privacy

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Models](#models)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [Features](#features)
- [License](#license)
- [Contact](#contact)

## Introduction
Privacy is application which detects and masks any PII data present in Unstructured, Text, Image, DICOM, Video and returns the processed data.
 
## Requirements
1. Python 3.11
2. VSCode
3. Mongo DB

# Models
 1. En_core_wb_lg and en_core_web_trf Model Download and place it lib folder:
     link:[https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl](https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl) 
    link:[https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl](https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl)
     docs: https://spacy.io/models/en#en_core_web_lg
    
 2. StarPII Model for code moderation: https://huggingface.co/bigcode/starpii
    Download the model files, paste the model creating folder named as nermodel inside, src\privacy\util\code_detect\ner\pii_inference\nermodel
    
 3. Roberta multilingual ner model : https://huggingface.co/julian-schelb/roberta-ner-multilingual
    Create a folder named as "multilingual-ner" in responsible-ai-privacy\models directory. Download the files (config.json,special_tokens_map.json,tokenizer.json,tokenizer_config.json,unigram.json,pytorch_model.bin) from the provided link and place them in this folder (responsible-ai-  
    privacy\models\multilingual-ner).
    
 4. Roberta NER Model": https://huggingface.co/51la5/roberta-large-NER
   Create a folder named as "roberta" in responsible-ai-privacy\models directory. Download the files (config.json,pytorch_model.bin,sentencepiece.bpe.model,tokenizer.json)from the provided link and place them in this folder (responsible-ai-  
   privacy\models\roberta).
   
 5. PIIRanha NER Model: https://huggingface.co/iiiorg/piiranha-v1-detect-personal-information
   Create a folder named as "PIIRanha" in responsible-ai-privacy\models directory. Download the files (added_tokens.json,config.json,model.safetensors,special_tokens_map.json,spm.model,tokenizer.json,tokenizer_config.json,training_args.bin) from the provided link and place them in this folder (responsible-ai-  
   privacy\models\PIIRanha).
   


## Installation
To run the application, first we need to install Python and the necessary packages:
 
1. Install Python (version 3.11.x) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.
 
2. Install MongoDB by following the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/).
 
3. Install `pip` if it is not already installed. You can download and install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/).

4. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

5. Navigate to the `responsible-ai-privacy` directory:
    ```sh
    cd responsible-ai-privacy
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

8. Go to the `responsible-ai-privacy\responsible-ai-privacy` directory where the `lib` folder is present. From [Link](https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl) download the en_core_web_lg and paste the whl file inside the lib folder. 
Link provided above will directly download the model version 3.7.1. 

*If you download and use the other version of en_core_web_lg then make sure to change the name in the requirement.txt too. To download other version, visit [spaCy](https://spacy.io/models/en/#en_core_web_lg)

9. Now go back to `responsible-ai-privacy\responsible-ai-privacy` to install the requirements by running the following command : 
  Update the pip :
  ```sh
  python -m pip install pip==24.2
  ```
  Dowload the requirements : 
  ```sh
     pip install -r .\requirements\requirement.txt
  ```
  Special installations : 
  ```sh
      pip install fastapi==0.100.1
      pip install pydantic==1.10.11
      pip install datasets==2.15.0
      pip install numpy==1.26.2
      pip install torch==2.3.1
  ```
  Note: If you face any issue with the torch library then uninstall the torch `pip uninstall torch` and then reinstall the latest version `pip install torch` .
  Note:To anonymize PDF file which is part of privacyfiles_main please install PyMuPDF (which is a AGPL Licensed package) using following command:
  ```sh
     pip install PyMuPDF
   ```

Download and install the tesseract in your system. After installation, set the tessaract path in environment variables of account or system : [Tessaract](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.3.0.20221214.exe).
  Different versions of tesseract : [Versions](https://digi.bib.uni-mannheim.de/tesseract/).
  Tesseract Github : [Github](https://github.com/tesseract-ocr/tessdoc).



## Set Configuration Variables
After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `privacy` directory:
    ```sh
    cd src/privacy
    ```

2. Locate the `.env` file, which contains keys like the following:

   ```sh
   TELE_FLAG="${tele_flag}"  # [Mandatory]* False if do not want to connect with telemetry
   PRIVACY_TELEMETRY_URL = "${privacytelemetryurl}" # [Optional]- if teleflag=False otherwise provide the telemetry url
   PRIVACY_ERROR_URL = "${privacyerrorurl}" # [Optional]** - if teleflag=False otherwise provide the error url
   ADMIN_CONNECTION="${adminconnection}"  # [Optional] True if wants to connect to Admin module 
   PRIVADMIN_API="${adminapi}" # Optional if adminconnection is not True otherwise provide Admin url
   AUTH_TYPE = "${authtype}"            # [Optional]   Options: azure , jwt , none (bydefault)
   SECRET_KEY = "${secretkey}"          # [Optional]  Secret key for JWT token
   AZURE_CLIENT_ID="${azureclientid}"   # [Optional]
   AZURE_TENANT_ID="${azuretenantid}"   # [Optional]
   AZURE_AD_JWKS_URL = "${azuread_jwks_url}" # [Optional] 
   API_KEY="${api_key}"                    # [Optional] required if using computer vision
   API_ENDPOINT="${api_endpoint}"          # [Optional] required if using computer vision
   GCS_DEVELOPER_KEY="${gcsdeveloperkey}"  # [Optional] required if using computer vision
   VERIFY_SSL = "${verify_ssl}" #[Optional] If you want to by pass verify SSL check then set the variable    value to False otherwise True

   ```
    
    *TELE_FLAG is made true only if user wants to request the response in telemetry. Otherwise for the normal flow it can be set as False.
    For Telemetry setup, refer this link [responsible-ai-telemetry](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/tree/master/responsible-ai-telemetry)
    set the below env variables for connecting with telemetry alongside Telemetry flag.
   
   ```sh
    TELEMETRY_FLAG="True"
    PRIVACY_TELEMETRY_URL="http://<host:PORT>/path/v1/telemtry/<privacy telemetry api url>"
    PRIVACY_ERROR_URL="http://<host:PORT>/path/v1/telemtry/<privacy error telemetry api url>"
   ```

  ### HTTP Security Headers Configuration

    ```sh
    allow_methods = "${allow_methods_example}" #[Mandatory] e.g., "*" or "GET, POST, OPTIONS"
   allow_origin = "${allow_origin_example}"    # [Mandatory]e.g., '["http://localhost:8000/", "https://yourdomain.com"]'
   content_security_policy = "${csp_example}"  # [Mandatory]e.g., "default-src 'self'; script-src 'self' https://trusted.cdn.com"
   cache_control = "${cache_control_example}"  # [Mandatory]e.g., "no-cache, no-store, must-revalidate"
   XSS_header = "${xss_header_example}"  # [Mandatory]e.g., "1; mode=block"
   Vary_header = "${vary_header_example}"  # [Mandatory]e.g., "Origin"
   X-Frame-Options = "${x_frame_options_example}" # [Mandatory]e.g., "SAMEORIGIN" or "DENY"
   X-Content-Type-Options = "${x_content_type_options_example}" #[Mandatory] e.g., "nosniff"
   Pragma = "${pragma_example}" # [Mandatory]e.g., "no-cache"
    ```

    
    **Admin Module is the supporting module which is used for configuring the main module. User can create recognizer,custome templates, configure Thresholds and map it to created account and portfolio.

   Note: To utilize Computer Vision in Privacy , need a Azure Computer Vision Subscription and set the Endpoint,Key in .env file 

4. Replace the placeholders with your actual values.

## Running the Application

Before running the application:

Note: We are currently working on anonymizing PDF content, which will be available in the next release.
Please comment out the PDF anonymize router (from privacy.service.pdf_service import PDFService) and the privacy file anonymize router (@fileRouter.post('/privacy-files/anonymize')) with its respective import statements (i.e., linenumber 1319-1384 and 1546-1621 in [privacy_router.py](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/blob/master/responsible-ai-privacy/responsible-ai-privacy/src/privacy/routing/privacy_router.py) file), also comment the [pdf_service.py](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/blob/master/responsible-ai-privacy/responsible-ai-privacy/src/privacy/service/pdf_service.py)file.

Once we have completed all the aforementioned steps, we can start the service.

1. Navigate to the `src` directory:
    ```sh
    cd ..
    ```

2. Run main file:
    To run privacy_main :
    ```sh
    python privacy_main.py
     ```
    To run privacyfiles_main* :
    ```sh
    python privacyfiles_main.py
     ```

    *Privacyfiles is used for accessing data from files like excel, pdf, video etc.

3. Open the following URL in your browser:
    For privacy_main :
    [http://localhost:30002/v1/privacy/docs#/](http://localhost:30002/v1/privacy/docs#/)
        User can also change the port which is mentioned in privacy_main.py file

    For privacyfiles_main :
    `http://localhost:<portnumber>/rai/v1/privacy-files/docs#/`
        User can also change the port which is mentioned in privacyfiles_main.py file
    
    Note: For the video anonymize endpoint (rai/v1/privacy-files/video/anonymize) use ocr as "Tesseract".
   
 
   
## Features

**Privacy :** 
<table>
  <tr>
    <th>API NAME</th>
    <th>DESCRIPTION</th>
  </tr>
  <tr>
    <td>Analyze</td>
    <td>Detect PII entities in text.</td>
  </tr>
  <tr>
    <td>Anonymize</td>
    <td>Anonymizing detected PII text entities.</td>
  </tr>
  <tr>
    <td>Encrypt</td>
    <td>Encrypt the PII using a given key.</td>
  </tr>
  <tr>
    <td>Decrypt</td>
    <td>Decrypt the encrypted PII in the text using the encryption key.</td>
  </tr>
  <tr>
    <td>Image Analyze</td>
    <td>Detect the PII entities in an Image.</td>
  </tr>
  <tr>
    <td>Image Anonymize</td>
    <td>Anonymize detected PII entities in an Image.</td>
  </tr>
  <tr>
    <td>Image Mask</td>
    <td>Replace the PII with a given character in an Image.</td>
  </tr>
  <tr>
    <td>Image Hashify</td>
    <td>Hashes the PII text present in an Image.</td>
  </tr>
  <tr>
    <td>Dicom Anonymize</td>
    <td>Anonymize PII entities in medical x-ray images.</td>
  </tr>
  <tr>
    <td>Code Redaction</td>
    <td>Anonymize PII entities in code text.</td>
  </tr>
  <tr>
    <td>Code Anonymize</td>
    <td>Anonymize PII entities in code file.</td>
  </tr>
  <tr>
    <td>Diff Privacy File</td>
    <td>Load csv file and gives the column name which can be used in further api.</td>
  </tr>
  <tr>
    <td>Diff Privacy Anonymize</td>
    <td>Using the column name, user can apply differential privacy.</td>
  </tr>
</table>

**Privacy Files :**

<table>
  <tr>
    <th>API NAME</th>
    <th>DESCRIPTION</th>
  </tr>
  <tr>
    <td>Excel Anonymize</td>
    <td>Anonymize PII entities in excel file.</td>
  </tr>
  <tr>
    <td>Video Anonymize</td>
    <td>Anonymize PII entities in video.</td>
  </tr>
</table>

## License

The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.

## Contact

If you have more questions or need further insights, feel free to Connect with us @ infosysraitoolkit@infosys.com
