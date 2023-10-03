# Deploying to Azure Function App walkthrough

Walkthrough of creating an Azure Functions Project locally (from VSCode) and deploying it to Azure Functions App in Azure. This project gets data from an API, processes it, then send the data to Event Hub using Azure Key Vault to manage connection strings.

## Getting started

### Spin up resources in Azure
In Azure, you will need the following resources setup:
- Azure Functions App (will host your functions)
- Azure Key Vault (for managing connection strings)
- Azure Event Hub (will recieve data from Azure Functions App)
- Azure Storage Account (used to store various artifacts and data related to your functions, such as function triggers, logs, and state)

### Setup Event Hub policies and store as secrets in Key Vault
Within Azure Event Hub, you will need to setup a policy for sending data to Event Hub. You could call this policy something like `AzureFunctionsApp-sender`, and set is as a 'Send' claim. This policy will permit Azure Functions App to send data to Event Hub. Copy the policy value (access key) to Azure Key Vault as a secret. The secret value should look something like this: `<Endpoint=ENDPOINT>://<NAME_SPACE>.servicebus.windows.net/;SharedAccessKeyName=<KEY_NAME>;SharedAccessKey=<KEY_VALUE>;`. Name the secret.

### Store environment variables in Azure Functions App
Any private variables your code uses should be stored in application settings of Azure Functions App (go to the configuration tab). These variables should be stored as a value and be given a name thats used to access that value. For example, you should store the name of the secret (that contains the policy string for sending data to Event Hub) as a value under the name "Secretname". You will also need to store the name of the Key Vault as a value under the name "VaultName", and the Event Hub name as a value under the name "EventHubName". If you used an API that requires a key, hten you should store the key value under the name "ApiKey". When you come to deploy you Azure Functions Project, you access these private variables from Azure Functions App.

<b>Store private variables in config.ini when deveoping locally</b>
<br>
When developing Azure Functions (function_app) locally, you will not be able to access any private variables stored in the application settings of Azure Functions App. Instead, you can supply these variables (such as the Vault Name and Secret Name) using a `config.ini` file. When you deploy the project to Azure, you will need to replace the variables imported from `config.ini` with those stored in application settings of Azure Functions App ("SecretName", "VaultName", "EventHubName", "ApiKey").


For example, in development your variable import may look like this:
```
import configparser as ConfigParser

config = ConfigParser()
config.read("config.ini")
ACCESS = config["ACCESS"]

SECRET_NAME = ACCESS["SECRET_NAME"]
VAULT_NAME = ACCESS["VAULT_NAME"]
EVENTHUB_NAME = ACCESS["EVENTHUB_NAME"]
API_KEY = ACCESS["API_KEY"]
```

Your `config.ini` file would look like:
```
[ACCESS]
SECRET_NAME = "your_secret_name"
VAULT_NAME = "your_vault_name"
EVENTHUB_NAME = "your_eventhub_name"
API_KEY ="your_api_key"
```

For deployment, these variables would be obtained from Azure Function App configuration environment instead:
```
import os

SECRET_NAME = os.environ["SecretName"]
VAULT_NAME = os.environ["VaultName"]
EVENTHUB_NAME = os.environ["EventHubName"]
API_KEY = os.environ["ApiKey"]
```

### Install Technology Stack for local development
The following technologies are required to create an Azure Functions Project in VSCode:
- [Python](https://www.python.org/)
- Visual Studio Code (VSCode)
- [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools#installing)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/)

In VSCode, you will need to install the following extensions:
- Azure Tools

### Setup Python Virtual Environment
You will need to set up a Python Virtual Environment called `azure-func-env` in the root directory of the project folder, and download all the required packages to this environment using the requirements.txt file. This environment is used to develop the functions locally. Note that, when you deploy your functions to Azure, you will need to provide a seperate `requirements.txt` file that is compatible with Azure's Linux OS, hence why there is a seperate `requirements.txt` file exists in the "AzureFunctionsProject" folder.

Setup Python environment from Windows CMD:
1. Navigate to project directory: `<path_to/Azure-Functions-App>`
2. Create python environment: `python -m venv azure-func-env`
3. Activate environment: `azure-func-env\Scripts\activate`
4. Install required dependencies to environment using requirement.txt: `pip install -r requirements.txt`

If you need to manually install any packages then use `pip install <package name>`.

## Set up a local Azure Functions Project
Before you can deploy your local Python functions to Azure Functions App, you have to create an Azure Functions Project first. Azure Functions Project contains a set of files and configurations that enable you to create, develop, test, and deploy serverless functions to Microsoft Azure.

To create an Azure Functions Project and add your local functions, do the following:
1. Create a folder to contain your Azure Functions Project, e.g., "AzureFunctionsProject"
2. Open the Command Palette and search for `Azure Functions: Create New Project..`
3. It will ask you to...
    - Choose a directory for the project -> "AzureFunctionsProject"
    - Type of trigger to use -> here we use timer trigger
    - Name of trigger -> here we call it stream_to_eventhub
    - Python interpreter -> you want to point to your local virtual environment <path_to/azure-func-env>

The final project structure for an Azure Functions Project should look something like this:
```
    AzureFunctionsProject/
        .funcignore
        .gitignore
        .venv
        requirements.txt
        host.json
        local.settings.json
        function_app.py
        utils.py
```

- `function_app.py` contains the function code that performs specific task(s) when triggered. In this project, the code gets data from an API and sends this data to Event Hub.
- `requirements.txt` contains a list of dependencies (packages) that the function code relies on to run. Azure is Linux OS so make sure your packages are all Linux compatible if you are developing in a Windows environmnet (e.g., pywin32 is not compatible with Azure).
- `host.json` contains global configuration settings for the Azure Functions host. You should not need to edit this file.
- `local.settings.json` stores application settings and connection strings for when you are developing and running your functions locally. Here, you can supply the connection string to your storage account as string a value to the key "AzureWebJobsStorage".
- `utils.py` contains utility functions that are used by the Azure Function (function_app).

<b>Utility functions<b>
The functions in `utils.py` are used to perform the following steps:
1. Connect to Azure Vault and get connection string (for connecting to Event Hub)
2. Get data from API
3. Process and format data
4. Connect and send data to Event Hub 

<b>Dependencies</b>
The following [Azure PIP packages](https://pypi.org/project/azure/) are used throughout this project:
 - azure-core
 - azure-eventhub
 - azure-keyvault-secrets
 - azure-identity
 - websocket-client
 - [azure-functions](https://pypi.org/project/azure-functions/)

