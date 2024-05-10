from loguru import logger
from subprocess import PIPE, Popen
from os import system
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from socket import gethostname

from src.utils.config.config import KAFKA_TOPIC_TO, KAFKA_TOPIC_FROM, KAFKA_PORT


def run_all_file():
    try:
        files = (
            "src/web_server/server_core.py", "src/utils/dashboard_controller/board_api.py",
            "src/controller_db/source.py"
        )
        for file in files:
            Popen(args=["start", "python", file], shell=True, stdout=PIPE)
        logger.info("The files started working in their terminals.")
        return True
    except Exception as ex:
        logger.exception(ex)
        return False


def run_alembic_migration():
    try:
        flag = True
        if system("cd src && alembic upgrade head") != 0:
            flag = False
            logger.error("Error on alembic migration.")
    except Exception as ex:
        logger.exception(ex)
        flag = False
    return flag


def run_docker():
    try:
        logger.info("Building and running the entire application.")
        flag = True
        if system("docker compose -f src/docker/docker-compose.yml up -d") != 0:
            flag = False
            logger.error("Error on docker container creation.")
    except Exception as ex:
        logger.exception(ex)
        flag = False
    return flag


def init_kafka_topic():
    try:
        logger.info("Start create topics")
        admin_client = KafkaAdminClient(bootstrap_servers=f"localhost:{KAFKA_PORT}", client_id=gethostname())
        if not len(admin_client.list_topics()):
            admin_client.create_topics(
                new_topics=[NewTopic(name=KAFKA_TOPIC_TO, num_partitions=2, replication_factor=1)],
                validate_only=False)
            admin_client.create_topics(
                new_topics=[NewTopic(name=KAFKA_TOPIC_FROM, num_partitions=2, replication_factor=1)],
                validate_only=False)
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    # if run_docker():
    #     logger.info("Program will sleep for 10 second. While docker container initializing")
    #     sleep(10)
    #     if run_alembic_migration():
    #         init_kafka_topic()
    #         run_all_file()
    run_all_file()
