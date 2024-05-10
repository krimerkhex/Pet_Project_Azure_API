import time

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from time import sleep
from src.utils.config.config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, AZURE_PROJECT_NAME, KAFKA_PORT, \
    KAFKA_TOPIC_TO, KAFKA_TOPIC_FROM
from src.utils.config.table_models import Users, Tasks, Achievement
import kafka
from json import loads
from loguru import logger

engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}')


def add_or_update_users(users, session):
    for user_name in users:
        user = session.query(Users).filter_by(Name=user_name).first()
        if not user:
            user = Users(Name=user_name)
            session.add(user)

    session.commit()


def add_or_update_tasks(work_items, session):
    for task_data in work_items:
        user = session.query(Users).filter_by(Name=task_data['Assigned To']).first()
        if not user:
            user = Users(Name=task_data['Assigned To'])
            session.add(user)

        task = session.query(Tasks).filter_by(ID=task_data['ID']).first()
        if not task:
            task = Tasks(
                ID=task_data['ID'],
                Type=task_data['Type'],
                Title=task_data['Title'],
                user=user
            )
            session.add(task)
        else:
            task.Type = task_data['Type']
            task.Title = task_data['Title']
            task.user = user

        task.Status = task_data['Status']
        task.Reason = task_data['Reason']

    session.commit()


def add_or_update_achievement(achievements, session):
    for achievement in achievements:
        user = session.query(Users).filter_by(Name=achievement['Assigned To']).first()
        if not user:
            user = Users(Name=achievement['Assigned To'])
            session.add(user)

        check = session.query(Achievement).filter_by(
            Title=achievement['Title'],
            User_ID=user.ID
        ).first()

        if not check:
            achievement = Achievement(
                Title=achievement['Title'],
                Description=achievement.get('Description', ''),
                user=user
            )
            session.add(achievement)

    session.commit()


def send_message_to_kafka():
    producer = kafka.KafkaProducer(bootstrap_servers=[f"localhost:{KAFKA_PORT}"])
    producer.send(topic=KAFKA_TOPIC_TO, key=AZURE_PROJECT_NAME.encode(), value="get_revision".encode())
    producer.close()
    logger.info("Message from kafka sended")


def get_message_from_kafka(consumer: kafka.KafkaConsumer):
    logger.info("Start polling messages from kafka")
    work_items, users_in_project = [], []
    while len(work_items) == 0 or len(users_in_project) == 0:
        message = consumer.poll(timeout_ms=1.0)
        if len(message.keys()) != 0:
            for key in message:
                for record in message[key]:
                    key = record.key.decode("utf-8")
                    if key == "Work Item":
                        work_items.append(loads(record.value.decode("utf-8")))
                    elif key == "User":
                        users_in_project.append(record.value.decode("utf-8"))
    logger.info(f"Get from kafka: {len(work_items)} items and {len(users_in_project)} users")
    return work_items, users_in_project


def fulling_database():
    Session = sessionmaker(bind=engine)
    consumer = kafka.KafkaConsumer(KAFKA_TOPIC_FROM, bootstrap_servers=f"localhost:{KAFKA_PORT}",
                                   enable_auto_commit=True,
                                   auto_offset_reset='latest')
    session = Session()

    send_message_to_kafka()
    work_items, users_in_project = get_message_from_kafka(consumer)
    add_or_update_users(users_in_project, session)
    add_or_update_tasks(work_items, session)
    add_or_update_achievement(
        [{"ID": "1", "Assigned To": "Коля Гареев", "Title": "First steps", "Description": "Finished first task"}],
        session)
    session.close()
    consumer.close()


def update_task_table():
    Session = sessionmaker(bind=engine)
    session = Session()
    consumer = kafka.KafkaConsumer(KAFKA_TOPIC_FROM, bootstrap_servers=f"localhost:{KAFKA_PORT}",
                                   enable_auto_commit=True,
                                   auto_offset_reset='latest')
    send_message_to_kafka()
    work_items, users_in_project = get_message_from_kafka(consumer)
    add_or_update_tasks(work_items, session)
    session.close()
    consumer.close()


def start_back_server():
    logger.info("Module ready. Start init databases")
    sleep(1)
    fulling_database()
    while True:
        logger.info("Module go to 1 minute sleep")
        sleep(60)
        logger.info("Time to update database")
        update_task_table()


if __name__ == "__main__":
    logger.info("source.py")
    start_back_server()
