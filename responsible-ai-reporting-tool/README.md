# responsible-ai-reporting-tool

## Table of content
- [Introduction](#introduction)
- [Installation](#installation)
- [Set Configuration Variables](#set-configuration-variables)
- [Running the Application](#running-the-application)
- [License](#license)
- [Contact](#contact)



## Introduction
The `responsible-ai-reporting-tool` repository is used for generating of the reports from the various modules in the format specified.


## Installation
To run the application, first we need to install Python and the necessary packages:

1. Install Python (version ==3.11.4) from the [official website](https://www.python.org/downloads/) and ensure it is added to your system PATH.

2. Install MongoDB by following the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/).

3. Install `pip` if it is not already installed. You can download and install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/).

4. Install "wkhtmltopdf" (version >= 0.12.5) Software  from the [official website](https://wkhtmltopdf.org/downloads.html) and ensure it is added to your system PATH.

5. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

6. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

7. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
         ```
    - On Linux/Mac:
        ```sh
        source venv/bin/activate

8. Navigate to the `responsible-ai-reporting-tool` directory:
    ```sh
    cd responsible-ai-reporting-tool
    ```

9. Go to the `requirements` directory where the `requirement.txt` file is present and install the requirements:
    ```sh
    pip install -r requirement.txt
    ```
## Set Configuration Variables

After installing all the required packages, configure the variables necessary to run the APIs.

1. Navigate to `src` directory:
    ```sh
    cd wrapper\src
    ```

2. Locate the `.env` file in the project directory. This file contains several configuration keys. Make sure to fill in the mandatory fields as shown below (sample values are provided for reference):

    ```sh
    DB_NAME = "${dbname}"                     # [Mandatory] DB_NAME = "raibackend"
    DB_USERNAME = "${username}"               # [Optional]
    DB_PWD = "${password}"                    # [Optional]
    DB_IP = "${ipaddress}"                    # [Optional]
    DB_PORT = "${port}"                       # [Optional]
    DB_TYPE ="${dbtype}"                      # [Mandatory] DB_TYPE = "mongo"
    MONGO_PATH = "mongodb://${DB_USERNAME}:${DB_PWD}@${DB_IP}:${DB_PORT}/"    # [Mandatory] MONGO_PATH = "mongodb://localhost:27017/"
    COSMOS_PATH = "${cosmos_path}"            # [Optional]
    PDF_CONTAINER_NAME = "${pdf_container_name}"   # [Optional] PDF_CONTAINER_NAME = "rai-pdf-reports"
    HTML_CONTAINER_NAME = "${html_container_name}" # [Optional] HTML_CONTAINER_NAME = "rai-html-reports"
    ZIP_CONTAINER_NAME = "${html_container_name}" # [Optional] ZIP_CONTAINER_NAME = "rai-zip-files"
    ```
    ```sh
    allow_origin = "${allow_origin}"     # ALLOW_ORIGINS ="*"       
    To allow access to all sites, use the value *. Alternatively, you can specify a list of sites that should have access.

    ```
3. Navigate to app/exception/exception.py under 'src':
   Add the below import statements:
   ```sh
   from fastapi.responses import JSONResponse
   from fastapi.encoders import jsonable_encoder
   ```
   Save it and proceed
   
   

## Running the Application
Once we have completed all the aforementioned steps, we can start the service.

1. Run `main.py` file:
    ```sh
    python main.py
    ```

2. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running:`http://localhost:80/v1/report/docs`

    User can also change the port which mentioned in main.py file


## License
The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.


## Contact
If you have more questions or need further insights, feel free to Connect with us @ Infosysraitoolkit@infosys.com
 
