
# responsible-ai-safety

## Introduction
Safety is an application which detects and masks any unsafe or harmful content present in Unstructured text and inappropriate content in the image and video.
 
## Requirements
1. Python 3.11
2. VSCode
3. MongoDB

## Installation
To run the application, first we need to install Python and the necessary packages:
 
1. Install Python (version 3.11.x) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.
   
2. Install MongoDB by following the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/).
 
3. Install `pip` if it is not already installed. You can download and install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/).
   
# Models needed

1. Detoxify model for Unstructured text: Download from https://huggingface.co/FacebookAI/roberta-base/tree/main 

   Now download the model checkpoint file from this url and keep it under this folder -
   toxic_model_ckpt_file (https://github.com/unitaryai/detoxify/releases/download/v0.3-alpha/toxic_debiased-c7548aa0.ckpt) 

   Name the folder as 'detoxify'.

2. NFSW model for image : https://github.com/GantMan/nsfw_model . You can download models from 
   https://s3.amazonaws.com/ir_public/ai/nsfw_models/nsfw.299x299.h5

   Place the file directly named as 'nsfw.299x299.h5'.

3. NSFW model for image : You can download model from 
   https://s3.amazonaws.com/ir_public/nsfwjscdn/nsfw_mobilenet2.224x224.h5

   Place the file directly named as 'nsfw_mobilenet2.224x224.h5'.

4. Codebert base Malicious model : You can download model from
   https://huggingface.co/DunnBC22/codebert-base-Malicious_URLs/tree/main

   Name the folder as 'codebert-base-Malicious_URLs'.

 Place the above model folders in a new folder named 'models' in the following way: 'responsible-ai-toxicity/models'.
 
## Set Configuration Variables
After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to the `profanity` directory:
    ```sh
    cd src/profanity
    ```

2. Locate the `.env` file, which contains keys like the following:

   ```sh
    ADMIN_API= "${adminapi}" # Optional if adminconnection is not True otherwise provide Admin url
    SAFETY_COFIG="${safetycofig}" # [Mandatory]* set value as '{"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.25,"sexy":0.25}' if not connect with admin module otherwise config this  value     through admin module. 
    IMAGEGEN_IP="${imagegenapi}"  # Need image generation api for genearting image from text. [Mandatory]* for Running 'api/v1/safety/profanity/imageGenerate' has dependency on LLM module.
    ADMIN_CONNECTION="${adminconnection}" # [Mandatory]* False if do not want to connect with Admin module, otherwise True.
    TELEMETRY_FLAG="${telemetryflag}"   # [Mandatory]* False if do not want to connect with telemetry.
   ```

    *TELE_FLAG is made true only if user wants to request the response in telemetry. Otherwise for the normal flow it can be set as False.
    For Telemetry setup, refer this link responsible-ai-telemetry
    set the below env variables for connecting with telemetry alongside Telemetry flag.
   
   ```sh
    TELEMETRY_FLAG="True"
    PROFANITY_TELEMETRY_URL="http://<host:PORT>/path/v1/telemtry/<profanity telemetry api url>"
   ```

    **Admin Module is the supporting module which is used for configuring the main module. User can create recognizer,custome templates, configure Thresholds and map it to created account and portfolio.

   **SSL Verify** : If you want to by pass verify SSL check then set the variable value to False otherwise True:
   ```sh
      verify_ssl=<set it to True or False as required>
      VERIFY_SSL="${verify_ssl}"
   ```

4. Replace the placeholders with your actual values.


## Steps to run this module :
1. Clone this repository in vscode
2. Create a virtual environment for python using cmd -
   `python -m venv <env-name>`
3. Activate the virtual environment:
    - On Windows:
        ```sh
        .\myenv\Scripts\activate
         ```
 
    - On Linux/Mac:
        ```sh
        source myenv/bin/activate
        ```
4. Activate the python virtual environment and install all the dependencies in requirement.txt file of the     cloned repository - Navigate to responsible-ai-toxicity and execute
   `pip install -r requirements\requirement.txt`
5. Open .env file in vscode and configure the entries in it
6. In the virtual environment go to src folder of cloned repository and run below command to run the module-
   ```sh
    python main.py
     ```

   Note: If you get any error like : "DDL load failed.Some module is missing" after executing main.py then it is due to compatability issues of onnxruntime version so try with different versions of onnxruntime e.g. onnxruntime==1.21.0 or onnxruntime==1.22.0.

3. PORT_NO : Use the Port No that is configured in `.env` file.

   Open the following URL in your browser:
`http://localhost:8001/api/v1/safety/docs`

Note: The '/api/v1/safety/profanity/imageGenerate' API is currently not working due to its dependency on the LLM module, DALL·E 2 subscription is required to use the endpoint /rai/v1/llm/image.


  
## License
The source code for the project is licensed under the MIT license, which you can find in the [LICENSE.txt](License.md) file.

## Open Source tools Used:
1. Detoxify model for Unstructured text
2. NFSW model for image
## Contact
If you have more questions or need further insights please feel free to connect with us @
Infosysraitoolkit@infosys.com
