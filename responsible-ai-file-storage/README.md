# responsible-ai-file-storage

## Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Features](#features)
- [Installation](#installation)
- [Configurations](#configurations)
- [How to Get GCP Credentials JSON File](#how-to-get-gcp-credentials-json-file)
- [License](#license)

## Introduction
This module provides a simplified, high-level interface for interacting with Azure Blob Storage, Google Cloud Storage (GCS), and AWS S3 Buckets. It encapsulates the complexities of the underlying SDKs for each cloud provider, offering convenient functions for common file operations such as uploading, downloading, listing, and deleting objects.

The wrapper aims to make working with cloud-based file storage more accessible and efficient by handling authentication, bucket/container management, and error handling internally. This allows users to focus on the core logic of their applications without needing to directly manage the low-level client objects or SDK intricacies.

By abstracting away provider-specific implementations, the module delivers a streamlined, consistent, and Pythonic experience across Azure, GCP, and AWS cloud platforms.

## Requirements
1. Python >= 3.11
2. pip
3. Azure Blob Storage
4. VSCode

## Features

### 🔹 Azure Blob Storage

- **Add File**  
  `POST /api/v1/azureBlob/addFile`  
  Uploads a file to a specified container in Azure Blob Storage.

- **Get File**  
  `GET /api/v1/azureBlob/getBlob`  
  Retrieves a file from a specified container in Azure Blob Storage.

- **Delete File**  
  `DELETE /api/v1/azureBlob/delete_blob`  
  Deletes a specific file from a container in Azure Blob Storage.

- **Update File**  
  `POST /api/v1/azureBlob/updateFile`  
  Replaces an existing file in a container with a new version.

- **Add Container**  
  `POST /api/v1/azureBlob/addContainer`  
  Creates a new container in Azure Blob Storage.

- **List Containers**  
  `GET /api/v1/azureBlob/List-Containers`  
  Retrieves a list of all containers in the Azure storage account.

---

### 🔹 Google Cloud Storage (GCP)

- **Add File**  
  `POST /api/v1/gcs/addFile`  
  Uploads a file to a specified bucket in Google Cloud Storage.

- **List Objects**  
  `GET /api/v1/gcs/{bucket_name}/listObjects`  
  Retrieves a list of all objects within the specified GCS bucket.

- **Get Object**  
  `GET /api/v1/gcs/getObject`  
  Downloads a specific object (file) from a GCS bucket.

- **Delete Object**  
  `DELETE /api/v1/gcs/deleteObject`  
  Deletes a specified object from a GCS bucket.

- **Update File**  
  `POST /api/v1/gcs/updateFile`  
  Replaces an existing object in a bucket with a new version.

- **List Buckets**  
  `GET /api/v1/gcs/listBuckets`  
  Lists all available buckets in the connected GCP project.

- **Add Bucket**  
  `POST /api/v1/gcs/addBucket`  
  Creates a new bucket in Google Cloud Storage.

- **Get Object Properties**  
  `GET /api/v1/gcs/getObjectProperties`  
  Retrieves metadata and properties of a specific object.

---

### 🔹 Amazon Web Services (AWS) S3

- **Upload File**  
  `POST /api/v1/s3/uploadFile`  
  Uploads a file to a specified AWS S3 bucket.

- **List Objects**  
  `GET /api/v1/s3/{bucket_name}/listObjects`  
  Retrieves a list of all objects in the specified S3 bucket.

- **Get Object**  
  `GET /api/v1/s3/getObject`  
  Downloads a specific file from an S3 bucket.

- **Delete Object**  
  `DELETE /api/v1/s3/deleteObject`  
  Deletes a specified file from an S3 bucket.

- **Update File**  
  `POST /api/v1/s3/updateFile`  
  Replaces an existing file in an S3 bucket with a new one.

- **List Buckets**  
  `GET /api/v1/s3/listBuckets`  
  Lists all available S3 buckets in the AWS account.

- **Create Bucket**  
  `POST /api/v1/s3/createBucket`  
  Creates a new bucket in AWS S3.

- **Get Object Properties**  
  `GET /api/v1/s3/getObjectProperties`  
  Retrieves metadata and properties of a specific object in S3.

For more details refer our [API Documentation](https://github.com/Infosys/Infosys-Responsible-AI-Toolkit/blob/Release-2.2.0/responsible-ai-file-storage/docs/File_Storage_API_Documentation.pdf)

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
3.	Install dependencies. 
      1. Go to **responsible-ai-file-storage\requirements** and run 
      ```bash 
         pip install -r requirements.txt.
      ```
      2. if you are on windows, please add **../** in front to .whl file in requirements.txt to install without any errors.
4. Add required configurations provided below in .env file.
5. Run the application using below steps:
      1. Go to responsible-ai-file-storage/src 
      2. Run 
      ```bash 
         python main.py 
      ```
6. Use the Port No that is mentioned in main.py file. Open the swagger URL in browser once server is running: `http://localhost:8000/api/v1/azureBlob/docs#/`


## Configurations
1. Add required environment variables.

| Key         | Placeholder Value | sample Value     | Required |
|-------------|-------------------|------------------|----------|
| AZURE_BLOB_STORAGE_CONNECTION_KEY    | "${azure_connection_key}" | YOUR_CONNECTION_KEY  |  yes     |
| GOOGLE_APPLICATION_CREDENTIALS    | "${google_application_credentials_path}"     | PATH TO JSON FILE WITH GCP KEYS DOWNLOADED FROM CLOUD CONSOLE  |  yes     |
| AWS_ACCESS_KEY_ID    | "${aws_access_key_id}"     | YOUR_CONNECTION_KEY  |  yes     |
| AWS_SECRET_ACCESS_KEY    | "${aws_secret_access_key}"     | YOUR_CONNECTION_KEY  |  yes     |
| AWS_SESSION_TOKEN    | "${aws_session_token}"     | YOUR_CONNECTION_KEY  |  yes     |
| allow_methods           | "${allow_methods}"      |       '["GET", "POST"]'           | yes |
| allow_origin            | "${allow_origin}"       |       ["*"]            | yes |
| content_security_policy | "${content_security_policy}"|  "default-src 'self'; img-src data: https:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"    | yes |
| cache_control           | "${cache_control}"      |      no-cache; no-store; must-revalidate            | yes |
| XSS_header              | "${xss_header}"         |    1; mode=block               | yes |
| Vary_header             | "${vary_header}"        |         Origin         | yes |
| X-Frame-Options         | "${X-Frame-Options}"    |            SAMEORIGIN       | yes |
| X-Content-Type-Options  | "${X-Content-Type-Options}" |     nosniff         | yes |
| Pragma                  | "${Pragma}"             |     no-cache             | yes |

## How to Get GCP Credentials JSON File

Follow these steps to download the service account JSON key and get the file path required to authenticate with Google Cloud Storage (GCS):

### Step-by-Step Guide

1. **Go to the Google Cloud Console**  
   Open [https://console.cloud.google.com/](https://console.cloud.google.com/) and log in with your Google account.

2. **Select Your Project**  
   In the top navigation bar, choose the GCP project where your Cloud Storage bucket exists (or create a new one).

3. **Open the IAM & Admin Section**  
   From the left sidebar, go to:  
   `IAM & Admin` ➝ `Service Accounts`

4. **Create a New Service Account (if needed)**  
   - Click on **"Create Service Account"**
   - Enter a name and description
   - Click **"Create and Continue"**

5. **Assign Roles**  
   - Assign the **"Storage Admin"** role (or a more restrictive role if needed)
   - Click **"Done"** after completing the permissions

6. **Generate a Key**  
   - In the service account list, click on the account you just created
   - Go to the **"Keys"** tab
   - Click **"Add Key"** → **"Create new key"**
   - Choose **JSON** as the key type
   - Click **"Create"** → the JSON key file will be downloaded automatically

7. **Move the JSON File to a Safe Location**  
   Store it securely in your project directory (e.g. `./secrets/gcp-key.json`)

8. **Get the Absolute Path**  
   Open a terminal and run the following command in the directory where your key is located:

   ```bash
   realpath ./secrets/gcp-key.json


## License

The source code for the project is licensed under MIT license, which you can find in the [LICENSE.md](LICENSE.md) file.
