from celery import Celery
from celery.utils.log import get_task_logger
from celery import shared_task
from .utils import Util
app = Celery('task',broker="amqp://guest:guest@localhost:5672")
logger = get_task_logger(__name__)

#(name="send_review_email_task")
@app.task
def send_review_email_task(data):
    logger.info("Sent review email")
    return Util.send_email(data)