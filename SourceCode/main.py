from MQTT.logger import logger
from MQTT.publisher import Publisher
import multiprocessing
from os import stat
import time
from multiprocessing import Process
import psutil


from AIPlanner.pddl import Solver
from AIPlanner.compriser import Interpret
from AIPlanner.executor import Execute
from AIPlanner.function_map import function_map
from MQTT.client import Client
from MQTT.subscriber import Subscriber
from MQDB.client import Client as MQDBClient

from camera_feed.player import Loop
from env.config import DATA_DIRECTORY

######### GLOBAL VARIABLES ##############

frequency = 2
state = [0, 0, 0, False]
PDDL_Directory = "/home/amey/MyVOL/UniStuttgart/Sem2/SCIoT/Project/repos/DEMO/PDDL"

live_feed_uri = "http://192.168.0.101:8080/video"

temperature_threshold = (20, 30)
luminance_threshold = (50, 70)

temperature_set = 22
temperature_delta = 1

brightness_set = 0
brightness_delta = 5

all_topics = [
    ("bpe/data/location/sensor/temperature", 1),
    ("bpe/data/location/sensor/luminance", 1),
    ("bpe/data/location/sensor/window", 1),
    ("bpe/data/location/sensor/humidity", 1),
]

temp_publisher_topic = "bpe/data/location/actuator/temperature"
luma_publisher_topic = "bpe/data/location/actuator/luminance"
#########################################

"""
    Initializations
"""


def init():
    mqtt_client = Client()
    solver = Solver(
        domain_path=PDDL_Directory,
        problem_path=PDDL_Directory,
        solution_path=f"{PDDL_Directory}/Plans",
        domain_file="BPE_Domain.pddl",
        problem_file="problem_file.pddl",
        problem_template=f"{PDDL_Directory}/problem_template.pddl",
        solution_filename="plan.txt",
        solver_uri="http://solver.planning.domains/solve",
    )
    InterP = Interpret(
        temperature_threshold=temperature_threshold,
        luminance_threshold=luminance_threshold,
    )
    return (mqtt_client, solver, InterP)


def init_publishers(mqtt_client: Client):
    temp_publisher = Publisher(client=mqtt_client, topic=temp_publisher_topic)
    luma_publisher = Publisher(client=mqtt_client, topic=luma_publisher_topic)

    temp_publisher.publisherVariable = temperature_set
    luma_publisher.publisherVariable = brightness_set

    return (temp_publisher, luma_publisher)


def init_mqdb(record_interval_seconds: int = 900):
    temp_mqdb_client = MQDBClient(
        table="temperatures",
        schema={"id": "num", "timestamp": "timestamp", "temperature": "num"},
        interval_seconds=record_interval_seconds,
    )
    temp_mqdb_client.bind_to_topic(topic=all_topics[0][0])

    luma_mqdb_client = MQDBClient(
        table="luminance",
        schema={"id": "num", "timestamp": "timestamp", "luminance": "num"},
        interval_seconds=record_interval_seconds,
    )
    luma_mqdb_client.bind_to_topic(topic=all_topics[1][0])

    humidity_mqdb_client = MQDBClient(
        table="humidity",
        schema={"id": "num", "timestamp": "timestamp", "humidity": "num"},
        interval_seconds=record_interval_seconds,
    )
    humidity_mqdb_client.bind_to_topic(topic=all_topics[3][0])

    return (temp_mqdb_client, luma_mqdb_client, humidity_mqdb_client)


"""
------------------------------------------------------------------------------------------------
"""


"""
    Create the Process Pool :          All necessary processes are created here
"""


def display_sunny_process(control: list):
    loop_sunny = Loop(
        file_path=f"{DATA_DIRECTORY}/video/Sunny.avi",
        control=control,
    )
    loop_sunny.play()


def show_live_feed_process(control: list):
    loop_live = Loop(file_path=live_feed_uri, control=control)
    loop_live.play()


mqdb_temp_client, mqdb_luma_client, mqdb_humidity_client = init_mqdb()


def run_mqdb(client: MQDBClient):
    client.get_mqtt_client().loop_forever()


process_list = {
    "sunny_process": Process(target=display_sunny_process, args=([True],)),
    "live_feed_process": Process(target=show_live_feed_process, args=([True],)),
    "run_mqdb_temp": Process(target=run_mqdb, args=(mqdb_temp_client,)),
    "run_mqdb_luma": Process(target=run_mqdb, args=(mqdb_luma_client,)),
    "run_mqdb_humidity": Process(target=run_mqdb, args=(mqdb_humidity_client,)),
}
"""
------------------------------------------------------------------------------------------------
"""

"""
    Create Necessary Callbacks :        All Callbacks especially MQTT 
"""


def callback(client, userdata, msg):
    if "temperature" in str(msg.topic):
        state[0] = float(str(msg.payload)[2:-1])

    if "luminance" in str(msg.topic):
        state[1] = float(str(msg.payload)[2:-1])

    if "window" in str(msg.topic):
        if "Open" in str(msg.payload):
            state[3] = True
        else:
            state[3] = False

    if "humidity" in str(msg.topic):
        state[2] = float(str(msg.payload)[2:-1])


"""
------------------------------------------------------------------------------------------------
"""

"""
    Create Necessary actions :          All Necessary Actions Taken here
"""


def increase_temperature(publisher: Publisher):
    global temperature_set
    publisher.publisherVariable = temperature_set + temperature_delta
    temperature_set = temperature_set + temperature_delta


def decrease_temperature(publisher: Publisher):
    global temperature_set
    publisher.publisherVariable = temperature_set - temperature_delta
    temperature_set = temperature_set - temperature_delta


def increase_brightness(publisher: Publisher):
    global brightness_set
    publisher.publisherVariable = brightness_set + brightness_delta
    brightness_set = brightness_set + brightness_delta


def decrease_brigthness(publisher: Publisher):
    global brightness_set
    publisher.publisherVariable = brightness_set - brightness_delta
    brightness_set = brightness_set + brightness_delta


def show_live_feed():
    logger.debug(
        f"show_live_feed : \t The Process is alive : {process_list['live_feed_process'].is_alive()}"
    )
    if not process_list["live_feed_process"].is_alive():
        stop_display()
        process_list["live_feed_process"] = Process(
            target=show_live_feed_process, args=([True],)
        )
        process_list["live_feed_process"].start()
    else:
        pass


def display_sunny():
    logger.debug(
        f"display_sunny : \t The Process is alive : {process_list['sunny_process'].is_alive()}"
    )
    if not process_list["sunny_process"].is_alive():
        stop_display()
        process_list["sunny_process"] = Process(
            target=display_sunny_process, args=([True],)
        )
        process_list["sunny_process"].start()
    else:
        pass


def stop_display(**kwargs):
    logger.debug(
        f"stop_display : \t trying to kill the processe {process_list['sunny_process']}, {process_list['live_feed_process']}"
    )
    if process_list["live_feed_process"].is_alive():
        process_list["live_feed_process"].terminate()
    if process_list["sunny_process"].is_alive():
        process_list["sunny_process"].terminate()


"""
------------------------------------------------------------------------------------------------
"""
"""
main :                                  All main calls go here:
"""


def main(
    mqtt_client: Client,
    solver: Solver,
    InterP: Interpret,
    temp_publisher: Publisher,
    luma_publisher: Publisher,
    function_map: dict,
):

    sub = Subscriber(
        client=mqtt_client,
        topic=all_topics,
        callback=callback,
    )
    mqtt_client.client.loop_start()
    time.sleep(frequency)
    mqtt_client.client.loop_stop()
    logger.debug(
        f"The current state is \t [temp, luma, humidity, window_status] = {state}"
    )

    replacement_dict, optimal = InterP.give_dict(
        temperature_val=state[0], luminance_val=state[1], window_status=state[3]
    )

    if optimal:
        logger.warning(f"Compriser is recognizing the current state as OPTIMUM!!")

    try:
        solver.generate_problem(replacement_dict=replacement_dict)
        solver.solve()

        executor = Execute(
            plan_path=f"{PDDL_Directory}/Plans/plan.txt",
            execution_map_dict=function_map,
        )
        executor.execute_plan()

    except Exception as e:
        logger.error(f"AI Planner has encountered an error!")
        logger.warning(f"Skipping the executions till the states change again")
        print(e)


if __name__ == "__main__":
    # Instantiate and Subscribe to the Necessary topics on MQTT
    mqtt_client, solver, InterP = init()
    temp_publisher, luma_publisher = init_publishers(mqtt_client=mqtt_client)

    # Run the MQDB processes:
    process_list["run_mqdb_temp"].start()
    process_list["run_mqdb_luma"].start()
    process_list["run_mqdb_humidity"].start()

    # Define Function Map

    function_map["increasetemperature"] = {
        "function": increase_temperature,
        "args": {"publisher": temp_publisher},
    }
    function_map["decreasetemperature"] = {
        "function": decrease_temperature,
        "args": {"publisher": temp_publisher},
    }
    function_map["increasebrightness"] = {
        "function": increase_brightness,
        "args": {"publisher": luma_publisher},
    }
    function_map["decreasebrightness"] = {
        "function": decrease_brigthness,
        "args": {"publisher": luma_publisher},
    }

    function_map["showlivefeed"] = {"function": show_live_feed, "args": {}}
    function_map["displaysunny"] = {"function": display_sunny, "args": {}}
    function_map["stopdisplay"] = {"function": stop_display, "args": {}}

    while True:
        main(
            mqtt_client=mqtt_client,
            solver=solver,
            InterP=InterP,
            temp_publisher=temp_publisher,
            luma_publisher=luma_publisher,
            function_map=function_map,
        )
        logger.debug(f"New plan executed at the frequency : {frequency}")

    process_list["run_mqdb_temp"].join()
    process_list["run_mqdb_luma"].join()
    process_list["run_mqdb_humidity"].join()
