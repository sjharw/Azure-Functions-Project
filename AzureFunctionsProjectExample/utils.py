# Import dependencies
import requests
import json
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventData
from azure.keyvault.secrets import SecretClient
from azure.eventhub.exceptions import AuthenticationError


def request_secret_key(vault_url: str, secret_name: str, credential = DefaultAzureCredential()):
    """
    Retrieves a secret value from Azure Key Vault.

    Args:
        vault_url (str): The URL of the Azure Key Vault.
        secret_name (str): The name of the secret to retrieve.
        credential: The credential used for authentication. Defaults to DefaultAzureCredential().

    Returns:
        secret.value (str): The secret value retrieved from Azure Key Vault.

    Raises:
        Exception: An error occurred if the secret retrieval fails.
    """
    secret_client = SecretClient(vault_url= vault_url , credential= credential)
    try:
        print(f"Attempting to retrieve your secret from Azure Key Vault...")
        secret = secret_client.get_secret(secret_name)
        print("Secret value succesfully retrieved")
        return secret.value
    except Exception as e:
        raise Exception("An error occurred:", e)


def get_api_data(api_url: str) -> dict:
    """
    Retrieve data from API. 

    Args:
        api_url(str): API url (include API key in the url if required).

    Returns:
        dict or None: A dictionary containing data if successful, or None if an error occurred.
    """
    response = requests.get(api_url)
    # Check if the response was successful
    if response.status_code == 200:
        print("Data retrieved successfully")
    else:
        response.raise_for_status()
    data = response.json()
    return data

def dict_to_str(data: dict) -> str:
    """
    Creates JSON string from dictionary.
    """
    json_string = json.dumps(data)
    return json_string

def send_data_to_eventhub(producer_client, data: str):
    """
    Send data to an Azure Event Hub using the provided producer client.

    Args:
        producer_client (EventHubProducerClient): The Event Hub producer client to use for sending data.
        data (str): The data to be sent to the Event Hub.

    Returns:
        None
    """
    try:
        # Create an event with the weather data
        event = EventData(body=data)
        # Send the weather event to the Event Hub
        producer_client.send_batch([event])
        # Print success message
        print("Event data successfully sent")
    except AuthenticationError as auth_error:
        # Handle the authentication error here, you can log or raise a custom exception
        print("Authentication Error! There is an issue with the credentials or tokens used for authentication." + 
              "This can happen if the connection string, shared access key, or token has expired or is incorrect." +
              "Check your connection string format, it should look like this: " + 
              "<Endpoint=ENDPOINT>://<NAME_SPACE>.servicebus.windows.net/;SharedAccessKeyName=<KEY_NAME>;SharedAccessKey=<KEY_VALUE>;EntityPath=<EVENT_HUB_NAME>")
        raise auth_error