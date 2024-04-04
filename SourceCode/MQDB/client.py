from os import set_blocking
import psycopg2
from MQTT.client import Client as MQTT_Client
from MQTT.subscriber import Subscriber as MQTT_Subscriber
import time

# import logger
from MQDB.logger import logger

# IMPORT POSTGRESQL ENV variables
from env.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASS,
    POSTGRES_DB,
)

# import custom exceptions
from MQDB.MQDDexceptions import *


detectionLists = {
    "numbers": ["INT", "INTEGER", "NUM", "NUMBER"],
    "strings": ["STRING", "STR", "CHAR", "CHARACTERS", "VARCHAR"],
}


class Client:
    def __init__(
        self,
        table: str,
        schema: dict,
        interval_seconds: int = 5,
        mqtt_client: MQTT_Client = None,
    ) -> None:
        """
        By default inserts in the table every 5 seconds

        schema example :
                            {
                                "id"    : "INTEGER"         <-      This will be added by default
                                "timestamp": "timestamp" ,
                                "value" : "INTEGER <OR VARCHAR ...>"
                            }
        """

        self.connection = self.__setup_connection()
        self.cursor = self.connection.cursor()

        # TABLE MANIPULATION
        self.table = table
        self.interval = interval_seconds * 1000
        self.i_time = self.__get_current_time_milis()

        # SCHEMA MANIPULATION
        self.schema_dict = schema
        self.schema_string = self.__get_schema_string(schema_dict=schema)

        # MQTT Client
        if mqtt_client == None:
            self.__mqtt_client = MQTT_Client()
        else:
            self.__mqtt_client = mqtt_client

        # INITIALIZATIONs
        try:
            self.__setup_table()
        except Exception as e:
            logger.error("MQDB : Client :: \t Probably the table already exists.")
            logger.error(f"MQDB : Client :: \t {str(TableAlreadyExists)}")
            logger.info(f"MQDB : Client :: \t Rolling back the previous entry")
            self.connection.rollback()

    def __get_current_time_milis(self):
        return round(time.time() * 1000)

    def __setup_connection(self):
        return psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASS,
            port=POSTGRES_PORT,
        )

    def __get_schema_string(self, schema_dict: dict):
        keys = list(schema_dict.keys())

        default_schema = "id serial not null"
        if "id" in keys:
            keys.remove("id")

        if "timestamp" in keys:
            keys.remove("timestamp")
            default_schema = str(
                f"{default_schema}, timestamp timestamp default current_timestamp"
            )

        custom_schema = default_schema

        for key in keys:
            if str(schema_dict[key]).upper() in detectionLists["numbers"]:
                parameter = str(f"{key} INTEGER")

            elif str(schema_dict[key]).upper() in detectionLists["strings"]:
                parameter = str(f"{key} VARCHAR")

            custom_schema = str(f"{custom_schema}, {parameter}")

        return custom_schema

    def __setup_table(self) -> None:
        logger.debug(f"MQDB : Client :\t Setting up the table")
        self.cursor.execute(f"CREATE TABLE {self.table}({self.schema_string});")
        self.__commit()

    def __commit(self) -> None:
        self.connection.commit()

    def release(self) -> None:
        self.connection.close()

    def __data_sanity_check(self, data: str) -> dict:
        data_list = list(data.split(", "))
        keys = list(self.schema_dict.keys())
        keys.remove("id")
        keys.remove("timestamp")
        if not (len(data_list) == len(keys)):
            raise SchemaSizeMismatch
            return None

        return dict(zip(keys, data_list))

    def __insert(self, data: str):
        data_dict = self.__data_sanity_check(data=data)
        keys = list(data_dict.keys())
        param_string = ""
        value_string = ""

        for index, key in enumerate(keys):
            if index == 0:
                param_string = str(f"{key}")
                value_string = str(f"{data_dict[key]}")
            else:
                param_string = str(f"{param_string}, {key}")
                value_string = str(f"{value_string}, {data_dict[key]}")

        query = str(f"INSERT INTO {self.table}({param_string}) VALUES({value_string});")
        logger.debug(f"MQDB : Client : Query :\t{query}")
        try:
            self.cursor.execute(query)
            logger.debug(f"MQDB : Client : Cursor executed")
            self.__commit()
        except Exception:
            logger.error(f"{str(InconsistantData)}")
            self.connection.rollback()

    def __is_good_time(self) -> bool:
        if self.interval < round(self.__get_current_time_milis() - self.i_time):
            self.i_time = self.__get_current_time_milis()
            return True
        return False

    def __calback(self, client, topic, msg):
        payload = str(msg.payload)[2:-1]
        if self.__is_good_time():
            try:
                self.__insert(payload)
            except Exception as e:
                raise DataInsersionFailed

    def bind_to_topic(self, topic: str):
        subscriber = MQTT_Subscriber(
            client=self.__mqtt_client, topic=topic, callback=self.__calback
        )

    def get_mqtt_client(self):
        return self.__mqtt_client.client
