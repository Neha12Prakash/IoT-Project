import time
from MQTT.client import Client
from MQTT.publisher import Publisher

cl = Client()


window_topic = "bpe/data/location/sensor/window"
pub = Publisher(client=cl, topic=window_topic, qos=0)

val = ["Closed"]
pub.runnable_publish(val=val, interval=0.1)
