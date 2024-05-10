from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from uvicorn import run
from src.controller_db.source import engine
from src.utils.config.table_models import Users, Achievement, Tasks
from loguru import logger
from sqlalchemy.orm import sessionmaker

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_clients_list():
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(Users).all()

    html = "<ul>"
    for user in users:
        html += f"<li><a href='/user/{user.ID}'>{user.Name}</a></li>"
    html += "</ul>"

    session.close()

    return HTMLResponse(content=html, status_code=200, media_type="text/html")


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def get_client_tasks(user_id: int):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(Users).filter_by(ID=user_id).first()

    if not user:
        return HTMLResponse(content="User not found", status_code=404, media_type="text/plain")

    html = f"<h1>{user.Name}</h1>"
    html += "<h2>Achievements</h2>"
    html += "<ul>"
    for achievement in user.achievements:
        html += f"<li>{achievement.Title} - {achievement.Description}</li>"
    html += "</ul>"

    html += "<h2>Tasks</h2>"
    html += "<ul>"
    for task in user.tasks:
        html += f"<li>{task.Title} - {task.Type} - {task.Status} - {task.Reason}</li>"
    html += "</ul>"
    session.close()

    return HTMLResponse(content=html, status_code=200, media_type="text/html")


def start_front_server():
    run(app)


if __name__ == "__main__":
    logger.info("server_core.py")
    start_front_server()
