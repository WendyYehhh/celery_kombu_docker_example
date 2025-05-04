import time

# Import the app instance directly from the celery_instance module
from celery_instance import app

@app.task(queue='quick_task')
def add(x, y):
    """
    A simple task that adds two numbers.
    """
    print(f"task: `add`, adding {x} and {y}")
    result = x + y
    print(f"Finished adding, result: {result}")
    return result


@app.task(queue='long_task')
def long_task(duration):
    """
    A task that sleeps for a given duration.
    """
    print(f"task: `long_task`, Sleeping for {duration} seconds")
    time.sleep(duration)
    result = f"Finished task sleeping for {duration} seconds"
    print(result)
    return result

# When `bind=True`, the task instance itself is passed as the first argument.
@app.task(bind=True, queue='default_queue')
def task_with_info(self, data):
    print(f"Task {self.name} called with args: {data}")
    print(f"Task id: {self.request.id}")
    print(f"Task name: {self.name}")
    print(f"Task data: {data}")
    print(f"Task args: {self.request.args}")
    print(f"Task kwargs: {self.request.kwargs}")
    print(f"Task chain: {self.request.chain}")
    print(f"Task errback: {self.request.errback}")
    print(f"Task callback: {self.request.callback}")
    return f"Task {self.request.id} finished"

if __name__ == '__main__':
    # Test the tasks
    add.delay(4, 4)
    long_task.delay(10)
    task_with_info.delay(data="Hello, World!")