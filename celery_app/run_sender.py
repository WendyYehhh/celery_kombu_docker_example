from .tasks import add, long_task, task_with_info
import time

if __name__ == '__main__':
    print("--- Starting to send Celery tasks ---")

    # 1. Send a simple addition task
    print("Sending add(4, 6)...")
    # .delay() = .apply_async()
    result_add = add.delay(4, 6)
    print(f"  -> Task sent, Task ID: {result_add.id}")

    time.sleep(0.5) # Wait a bit for easier log observation

    # 2. Send a long-running task
    print("Sending long_task(5)...")
    result_long = long_task.apply_async(args=[5]) # Use apply_async to pass more arguments
    print(f"  -> Task sent, Task ID: {result_long.id}")

    time.sleep(0.5)

    # 3. Send a task with info
    print("Sending task_with_info({'user': 'demo', 'value': 123})...")
    result_info = task_with_info.delay({'user': 'demo', 'value': 123})
    print(f"  -> Task sent, Task ID: {result_info.id}")

    print("--- All initial tasks have been sent ---")
    print("You can observe the worker logs to see the execution status.")
    print("Or try to retrieve the results later (if needed).")

    # Example: Wait and get results (Requires Redis Backend to be working correctly)
    # Note: In a production environment, you usually don't block the sender waiting for results
    try:
        print("Attempting to get 'add' task result (waiting up to 10 seconds)...")
        add_res_value = result_add.get(timeout=10)
        print(f"  -> 'add' task result: {add_res_value}")
    except Exception as e:
        print(f"  -> Could not get 'add' task result: {e}")

    try:
        print("Attempting to get 'long_task' task result (waiting up to 15 seconds)...")
        long_res_value = result_long.get(timeout=15)
        print(f"  -> 'long_task' task result: {long_res_value}")
    except Exception as e:
        print(f"  -> Could not get 'long_task' task result: {e}")

    try:
        print("Attempting to get 'task_with_info' task result (waiting up to 10 seconds)...")
        info_res_value = result_info.get(timeout=10)
        print(f"  -> 'task_with_info' task result: {info_res_value}")
    except Exception as e:
        print(f"  -> Could not get 'task_with_info' task result: {e}")

    print("--- Script execution finished ---")