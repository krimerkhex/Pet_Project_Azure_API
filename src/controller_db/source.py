from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.utils.dashboard_controller.board_api import get_board_data
from time import sleep
from src.utils.config.config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from src.utils.config.table_models import Users, Tasks, Achievement

engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}')

def add_or_update_users(users, session):
    for user_name in users:
        user = session.query(Users).filter_by(Name=user_name).first()
        if not user:
            user = Users(Name=user_name)
            session.add(user)

    session.commit()


def add_or_update_tasks(work_items, session):
    for task_id, task_data in work_items.items():
        user = session.query(Users).filter_by(Name=task_data['Assigned To']).first()
        if not user:
            user = Users(Name=task_data['Assigned To'])
            session.add(user)

        task = session.query(Tasks).filter_by(ID=task_id).first()
        if not task:
            task = Tasks(
                ID=task_id,
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


def fulling_database():
    Session = sessionmaker(bind=engine)
    session = Session()

    work_items, users_in_project = get_board_data()
    add_or_update_users(users_in_project, session)
    add_or_update_tasks(work_items, session)
    add_or_update_achievement([{"ID": "1", "Assigned To": "Коля Гареев", "Title": "First steps", "Description": "Finished first task"}], session)
    session.close()


def update_task_table():
    Session = sessionmaker(bind=engine)
    session = Session()
    work_items, users_in_project = get_board_data()
    add_or_update_tasks(work_items, session)
    session.close()


def start_back_server():
    fulling_database()
    while True:
        sleep(600)
        update_task_table()


if __name__ == "__main__":
    start_back_server()
