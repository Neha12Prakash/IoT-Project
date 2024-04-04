import os
from env.load_env import load_env


# Load the dot env file
root_path = os.path.dirname(os.path.abspath(__file__))
load_env(path=root_path + "/../.env")


# Declare all the exportable variables here
MQTT_HOST = str(os.environ.get("MQTT_HOST"))
MQTT_PORT = str(os.environ.get("MQTT_PORT"))
MQTT_USER = str(os.environ.get("MQTT_USER"))
MQTT_PASS = str(os.environ.get("MQTT_PASS"))

DATA_DIRECTORY = str(os.environ.get("DATA_DIRECTORY"))
SUBSYSTEM_PATH = str(os.environ.get("SUBSYSTEM_PATH"))

POSTGRES_HOST = str(os.environ.get("POSTGRES_HOST"))
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT"))
POSTGRES_USER = str(os.environ.get("POSTGRES_USER"))
POSTGRES_PASS = str(os.environ.get("POSTGRES_PASS"))
POSTGRES_DB = str(os.environ.get("POSTGRES_DB"))

OWM_KEY = str(os.environ.get("OWM_KEY"))
OWM_API_KEYS = str(os.environ.get("OWM_API_KEYS"))
