# Responsible AI – Admin

[![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-blue)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.0%2B-green)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# Responsible AI – Admin

### 🚀 Developer Quick Start

This guide helps you get **Responsible AI – Admin** running locally in minutes.

---

## Prerequisites

Make sure the following are installed:

* **Python** 3.9 – 3.11
* **MongoDB** (local or remote)
* **Git**
* **pip**

Optional but recommended:

* VS Code

---

## 1️⃣ Clone the Repository

```sh
git clone <repository-url>
cd responsible-ai-admin
```

---

## 2️⃣ Set Up Virtual Environment

```sh
python -m venv venv
```

Activate it:

* **Windows**

```sh
venv\Scripts\activate
```

* **Linux / macOS**

```sh
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```sh
cd responsible-ai-admin
pip install -r requirement/requirement.txt
```

---

## 4️⃣ Configure Environment Variables

Navigate to the config directory:

```sh
cd src/rai_admin
```

Create or update the `.env` file:

```env
# Database
DB_TYPE=mongo
DB_NAME=RAI_Admin_DB
MONGO_PATH=mongodb://localhost:<PORT_NUMBER>/

# OpenAI (if applicable)
OPENAI_MODEL=<model_name>
OPENAI_API_TYPE=<api_type>
OPENAI_API_BASE=<api_base>
OPENAI_API_KEY=<api_key>
OPENAI_API_VERSION=<api_version>

# RAG (required if RAG features are enabled)
RAG_IP=http://localhost:<PORT_NUMBER>

# CORS
allow_origin=*
allow_method=GET, POST, OPTIONS, HEAD, DELETE, PATCH, UPDATE
```

> 🔹 Replace placeholders with real values
> 🔹 For local MongoDB, ensure the port matches your MongoDB instance

---

## 5️⃣ Start the Application

Return to the `src` directory and run the app:

```sh
cd ..
python main.py
```

---

## 6️⃣ Verify the Service

Open Swagger UI in your browser:

```
http://localhost:<PORT_NUMBER>/api/v1/rai/admin/docs#/
```

If Swagger loads, the service is running successfully ✅

---

## 7️⃣ Enable Role-Based APIs (Required)

To use role-based endpoints:

* `/UpdateOpenAI`
* `/UpdateReminder`
* `/UpdateGoalPriority`
* `/getOpenAI`
* `/userRole`
* `/getRole`

### MongoDB Setup

Create a collection named **`OpenAIConfig`** and insert:

```json
[
  {
    "_id": 1697448919.0553722,
    "isOpenAI": true,
    "selfReminder": true,
    "isNemo": true,
    "role": "ROLE_ADMIN",
    "goalPriority": true
  },
  {
    "_id": 1697448919.0572698,
    "isOpenAI": true,
    "selfReminder": true,
    "isNemo": true,
    "role": "ROLE_USER",
    "goalPriority": true
  }
]
```

---

## Known Limitations

The following APIs are **not supported in the current release**:

* `/setCache`
* `/getEmbedings`
* `/clearEmbedings`
* `/deleteFile`

---

## Next Steps

* Explore APIs via Swagger UI
* Integrate with the core Responsible AI modules
* Configure deployment using Docker or Kubernetes

---

## Support

📧 **Infosys Responsible AI**
Email: **[Infosysraitoolkit@infosys.com](mailto:Infosysraitoolkit@infosys.com)**

---
