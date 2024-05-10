import time

import azure
from azure.devops.v7_1.core.core_client import CoreClient
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from src.utils.config.config import AZURE_TOKEN, AZURE_PROJECT_NAME, AZURE_ORGANIZATION_URL, KAFKA_PORT, KAFKA_TOPIC_TO, \
    KAFKA_TOPIC_FROM
from loguru import logger
import kafka
from json import dumps


def get_connection() -> azure.devops.connection.Connection:
    return Connection(base_url=AZURE_ORGANIZATION_URL, creds=BasicAuthentication("", AZURE_TOKEN))


async def azure_test_connection() -> bool:
    try:
        get_connection()
        return True
    except Exception as ex:
        logger.exception("Can't connect to azure devops server", ex)
        return False


def get_azure_project_id() -> str:
    connect = get_connection()
    core_client: CoreClient = connect.clients_v7_1.get_core_client()
    for project in core_client.get_projects():
        if project.name == AZURE_PROJECT_NAME:
            return project.id


def get_board_data() -> tuple[dict, list]:
    connect = get_connection()
    work_item_tracing_client: WorkItemTrackingClient = connect.clients_v7_1.get_work_item_tracking_client()
    work_items: dict = {}
    users_in_project: list = []
    i: int = 1
    while True:
        try:
            temp = work_item_tracing_client.get_revisions(i)[-1].as_dict()
            work_items[i] = {"ID": temp["id"],
                             "Title": temp["fields"]["System.Title"],
                             "Assigned To": temp["fields"]["System.AssignedTo"]["displayName"] if "System.AssignedTo" in
                                                                                                  temp[
                                                                                                      "fields"].keys() else "Unassigned",
                             "Type": temp["fields"]["System.WorkItemType"],
                             "Status": temp["fields"]["System.State"],
                             "Reason": temp["fields"]["System.Reason"]}
            logger.info("New work item:", work_items[i])
            if work_items[i]["Assigned To"] not in users_in_project:
                users_in_project.append(work_items[i]["Assigned To"])
                logger.info("New user:", work_items[i]["Assigned To"])
            i += 1
        except Exception as ex:
            logger.critical(ex)
            break
    return work_items, users_in_project


def get_message_from_kafka(consumer: kafka.KafkaConsumer):
    message = consumer.poll(timeout_ms=10.0)
    if len(message.keys()) != 0:
        for key in message:
            for record in message[key]:
                yield record.key.decode("utf-8"), record.value.decode("utf-8")
    yield None, None


def send_message_to_kafka(work_items, user_list):
    producer = kafka.KafkaProducer(bootstrap_servers=[f"localhost:{KAFKA_PORT}"])
    for item in work_items:
        producer.send(topic=KAFKA_TOPIC_FROM, key="Work Item".encode('utf-8'),
                      value=dumps(work_items[item]).encode('utf-8'))
    for user in user_list:
        producer.send(topic=KAFKA_TOPIC_FROM, key="User".encode('utf-8'), value=user.encode('utf-8'))
    producer.close()


def infinity_run():
    consumer = kafka.KafkaConsumer(KAFKA_TOPIC_TO, bootstrap_servers=f"localhost:{KAFKA_PORT}",
                                   enable_auto_commit=True,
                                   auto_offset_reset='latest')
    logger.info("Module ready. Start listen kafka topic")
    while True:
        for project, function_name in get_message_from_kafka(consumer):
            if project is not None and function_name is not None:
                if project == AZURE_PROJECT_NAME and function_name == "get_revision":
                    send_message_to_kafka(*get_board_data())


if __name__ == "__main__":
    logger.info("board_api.py")
    infinity_run()
