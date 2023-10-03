import logging
import datetime
from utils import request_secret_key, get_api_data, dict_to_str, send_data_to_eventhub
import azure.functions as func
from azure.eventhub import EventHubProducerClient, TransportType

#------- Get variables from Azure Functions App environment
import os

SECRET_NAME = os.environ["SecretName"]
VAULT_NAME = os.environ["VaultName"]
EVENTHUB_NAME = os.environ["EventHubName"]
API_KEY = os.environ["ApiKey"]

# Create vaul url string using vault name
vault_url = f"https://{VAULT_NAME}.vault.azure.net"

# Supply API URL of interest
api_url = "<api_of_interest>"

app = func.FunctionApp()

# This will setup a schedule for the timer trigger function to run
# The Cron Expression used here "* * * * * *" will run the function every minute
# This mimics data streaming
@app.schedule(schedule="* * * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 


def stream_to_eventhub(myTimer: func.TimerRequest) -> None:

    # Get current timestamp and log to console
    utc_timestamp = datetime.datetime.itcnow().replace(
        tzinfo= datetime.timezone.utc
    ).isoformat()
    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    if myTimer.past_due:
        logging.info('The timer is past due!')

    # Get the the Event Hub policy connection string
    # for the policy that allows you to send data to Event Hub
    # The secret string should look like this: "<Endpoint=ENDPOINT>://<NAME_SPACE>.servicebus.windows.net/;SharedAccessKeyName=<KEY_NAME>;SharedAccessKey=<KEY_VALUE>;"
    secret = request_secret_key(vault_url, SECRET_NAME)

    connect_str = secret + f"EntityPath={EVENTHUB_NAME}"

    producer_client = EventHubProducerClient.from_connection_string(connect_str, eventhub_name= EVENTHUB_NAME, transport_type= TransportType.AmqpOverWebsocket)

    data = get_api_data(api_url= api_url)

    # Data that is sent to Event Hub must serialized as JSON string
    data = dict_to_str(data)

    send_data_to_eventhub(producer_client, data)

    logging.info('Python timer trigger function executed.')