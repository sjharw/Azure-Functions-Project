# Azure Functions Project deployment walkthrough

Walkthrough of creating an Azure Functions Project locally (from VSCode) and deploying it to Azure Functions App in Azure. This project gives a template for getting data from an API, processing it, and sending the data to Event Hub, using Azure Key Vault to manage the connection strings.

## Setup Azure prerequisites

### Spin up resources in Azure
In Azure, you will need the following resources setup:
- Azure Functions App (will host your functions)
- Azure Key Vault (for managing connection strings)
- Azure Event Hub (will recieve data from Azure Functions App)
- Azure Storage Account (used to store various artifacts and data related to your functions, such as function triggers, logs, and state)

### Setup Event Hub policy and store as secret in Key Vault
Within Azure Event Hub, you will need to setup a Shared Access Policy for sending data to Event Hub. You could call this policy something like `AzureFunctionsApp-sender`, and set is as a 'Send' claim. This is referred to as a Shared Access Signature (SAS) token and it is used by a resource (in this case Azure Functions App) to authenticate the connection with Event Hub and send events to the Hub. 

Copy the SAS token to Azure Key Vault and store it under a named secret. The secret can be named "SecretName" and the value (SAS token) should look something like this: `<Endpoint=ENDPOINT>://<NAME_SPACE>.servicebus.windows.net/;SharedAccessKeyName=<KEY_NAME>;SharedAccessKey=<KEY_VALUE>;`.

## Install technologies for local development
The following technologies are required to create an Azure Functions Project in VSCode:
- [Python](https://www.python.org/)
- Visual Studio Code (VSCode)
- [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools#installing)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/)

In VSCode, you will need to install the following extensions:
- Azure Tools

## Store environmet variables securely

All private environment variables (such as the SAS token) should be stored in the application setting of Azure Functions App (see the resources configuration tab). When developing Azure Functions (function_app.py) locally, you will not be able to access any of the private variables stored in Azure Functions App. Instead, you can store and access these variables from the `local.settings.json` file in the root folder of the Azure Functions Project.

The variables required for this project include:
- Connection string for Storage Account
- Name of secret that contains SAS token (for authenticating connection to Event Hub)
- Name of the Key Vault (for connecting to Key Vault)
- Name of Event Hub Namespace (for connecting to Event Hub)
- API key (if a key is required to authenticate API request)

### Local development
Store all private variables in `local.settings.json` when developing locally.

Your `local.settings.json` file should look something like this:
```
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<storage_account_connection_string>",
    "VaultName": "<name_of_key_vault>",
    "EventHubName": "<name_of_eventhub>",
    "ApiKey": "<api_key>",
    "SecretName": "<name_of_secret_in_key_vault>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing"
  }
}
```

You can import these variables into function_app.py using `os.environ`:
```
import os

SECRET_NAME = os.environ["SecretName"]
VAULT_NAME = os.environ["VaultName"]
EVENTHUB_NAME = os.environ["EventHubName"]
API_KEY = os.environ["ApiKey"]
```

### For deployment
In deployment, all these private variables should be migrated to the application settings of Azure Functions App (see configuration tab). The variables should be stored using the same naming conventions ("AzureWebJobsStorage", "SecretName", "VaultName", "EventHubName", and "ApiKey"), and can be accessed by functions_app.py in the same way as local development (using `os.environ`).


## Set up a Azure Functions Project
Before you deploy your local Python functions to Azure Functions App, you have to create an Azure Functions Project first which will store you Azure Function and relevant files. Here, we have created a Azure Functions Project folder called "AzureFunctionsProjectExample" which is an example project.

To create an Azure Functions Project and add your local functions, do the following:
1. Create a folder to contain your Azure Functions Project, e.g., "AzureFunctionsProjectExample"
2. Open the Command Palette and search for `Azure Functions: Create New Project..`
3. It will ask you to...
    - Choose a directory for the project -> "AzureFunctionsProjectExample"
    - Type of trigger to use -> here we use timer trigger
    - Name of trigger -> here we call it stream_to_eventhub
    - Python interpreter -> you want to point to your local virtual environment (.venv)

The final project structure for an Azure Functions Project should look something like this:
```
    AzureFunctionsProjectExample/
        .funcignore
        .gitignore
        .venv
        requirements.txt
        host.json
        local.settings.json
        function_app.py
        utils.py
```

- `function_app.py` contains the function code that performs specific task(s) when triggered. In this project, the code gets data from an API and sends this data to Event Hub using the SAS token in Key Vault to authenticate.
- `requirements.txt` contains a list of dependencies (packages) that the function code relies on to run. Azure is Linux OS so make sure your packages are all Linux compatible if you are developing in a Windows environmnet (e.g., pywin32 is not compatible with Azure).
- `host.json` contains global configuration settings for the Azure Functions host. You should not need to edit this file.
- `local.settings.json` stores application settings and connection strings for when you are developing and running your functions locally. Here, you can supply the connection string to your storage account as string a value to the key "AzureWebJobsStorage". You can also store other values such as the Key Vault name, Event Hub name, Secret name, etc.
- `utils.py` contains utility functions that are used by the Azure Function (function_app.py).

<b>Utility functions</b>
<br>
The functions in `utils.py` are used to perform the following steps:
1. Connect to Azure Vault and get connection string (for connecting to Event Hub)
2. Get data from API
3. Process and format data
4. Connect and send data to Event Hub 

## Setup Python Virtual Environment
A virtual environment called `.venv` is automatically created when you create a Azure Functions Project, you can use this environment to run the functions locally. You can download all the required packages to this environment using the `requirements.txt` file from Windows CMD:
1. Navigate to Azure Functions Project directory: `<path_to/Azure-Functions-Project/AzureFunctionsProjectExample>`
2. Activate environment: `.venv\Scripts\activate`
3. Install required dependencies to environment using requirement.txt: `pip install -r requirements.txt`

If you need to manually install any packages then use `pip install <package name>`.

<b>Dependencies</b>
<br>
The following [Azure PIP packages](https://pypi.org/project/azure/) are used throughout this project:
 - azure-core
 - azure-eventhub
 - azure-keyvault-secrets
 - azure-identity
 - websocket-client
 - [azure-functions](https://pypi.org/project/azure-functions/)

## Run the function locally
To run the Azure Functions locally, you will need to authenticate your Azure account. You can do this via Azure CLI, simple open a powershell terminal in VSCode and run `az login`. This will take you to your Microsoft Azure login account. Once logged in, you should be able to run the functions locally from Windows CMD:

1. Navigate to your Azure Functions Project folder: `cd <path_to/Azure-Functions-Project/AzureFunctionsProjectExample>`
2. Activate virtual environmnet: `.venv/Scripts/activate`
3. Run the function: `func start --name <name_of_function>`

## Deploy Azure Function Project

To deploy your locally developed Azure Function project to the cloud, right click the Azure Function Project folder and click `Deploy to Function App...`. This will deploy your local Azure Functions Project to Azure Functions App.