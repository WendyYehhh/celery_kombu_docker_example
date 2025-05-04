from celery import Celery

# use service name: `rabbitmq` and `redis` since docker compose handle DNS parsing
BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'
RESULT_BACKEND = 'redis://redis:6379/0'

app = Celery(
    'celery_instance', 
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['tasks']
)


# optional
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    timezone='Asia/Taipei',
    enable_utc=True
)

# For local development to activate worker.
# In docker, activate by command defined in docker-compose.yml
if __name__ == '__main__':
    app.start()

