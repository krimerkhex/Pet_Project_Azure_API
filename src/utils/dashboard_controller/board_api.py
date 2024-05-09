import azure
from azure.devops.v7_1.core.core_client import CoreClient
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from src.utils.config.config import AZURE_TOKEN, AZURE_PROJECT_NAME, AZURE_ORGANIZATION_URL
from loguru import logger


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
            work_items[i] = {"Title": temp["fields"]["System.Title"],
                             "Assigned To": temp["fields"]["System.AssignedTo"]["displayName"] if "System.AssignedTo" in
                                                                                                  temp[
                                                                                                      "fields"].keys() else "Unassigned",
                             "Type": temp["fields"]["System.WorkItemType"],
                             "Status": temp["fields"]["System.State"],
                             "Reason": temp["fields"]["System.Reason"]}
            if work_items[i]["Assigned To"] not in users_in_project:
                users_in_project.append(work_items[i]["Assigned To"])
            i += 1
        except Exception as ex:
            logger.critical(ex)
            break
    return work_items, users_in_project


if __name__ == "__main__":
    data, users = get_board_data()
