# Celery, Kombu, and Docker Demo

This project demonstrates a basic Celery setup using RabbitMQ as the message broker and Redis as the result backend, all orchestrated with Docker Compose. It also includes Leek for monitoring the Celery cluster.

## Prerequisites

*   Docker ([Installation Guide](https://docs.docker.com/get-docker/))
*   Docker Compose ([Installation Guide](https://docs.docker.com/compose/install/))

## Directory Structure

```
celery_kombu_docker_example/
├── docker-compose.yml        # Defines and configures the services (RabbitMQ, Redis, Celery Worker, Leek)
├── celery_app/
│   ├── __init__.py
│   ├── celery_instance.py  # Defines the Celery App instance and configuration
│   ├── tasks.py            # Defines example Celery tasks (add, long_task, task_with_info)
│   ├── run_sender.py       # A script to send example tasks to the queue
│   ├── requirements.txt    # Python dependencies (Celery, Redis, Leek)
│   └── Dockerfile          # Builds the Docker image for the Celery worker and Leek
└── README.md               # This file
```

## How to Run

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repo-url>
    cd celery_kombu_docker_example
    ```

2.  **Build and start the services in detached mode:**
    ```bash
    docker compose up --build -d
    ```
    This command will:
    *   Build the Docker image defined in `celery_app/Dockerfile` (if not already built or if changes were made).
    *   Start containers for RabbitMQ, Redis, the Celery worker, and Leek based on `docker-compose.yml`.
    *   The `-d` flag runs the containers in the background.

3.  **Check container status:**
    ```bash
    docker compose ps
    ```
    You should see `rabbitmq_kombu_demo`, `redis_kombu_demo`, `celery_worker_kombu_demo`, and `leek_kombu_demo` running.

4.  **View worker logs:**
    ```bash
    docker compose logs -f worker
    ```
    You should see the Celery worker starting up and connecting to RabbitMQ and Redis. Press `Ctrl+C` to stop following logs.

## Sending Tasks

To send example tasks to the worker, run the `run_sender.py` script. You can execute it inside the running worker container or directly on your host if you have the prerequisites installed locally (though running inside the container ensures the correct environment).

**Option 1: Execute inside the worker container (Recommended)**

```bash
docker compose exec worker python run_sender.py
```

**Option 2: Run locally (Requires Python and dependencies from `requirements.txt`)**

```bash
python celery_app/run_sender.py
```

After running the sender script, check the worker logs (`docker compose logs -f worker`) again to see the tasks being received and executed.

## Components

*   **Celery:** Distributed task queue system. (`celery_app/`)
    *   `celery_instance.py`: Configures the Celery application, connecting to the broker and backend.
    *   `tasks.py`: Contains the actual task functions (`add`, `long_task`, `task_with_info`).
*   **RabbitMQ:** Message broker (using the `rabbitmq:3.11-management-alpine` image). Handles queuing tasks.
    *   Management UI: http://localhost:15672 (login with `guest`/`guest`)
*   **Redis:** Result backend (using the `redis:7-alpine` image). Stores the results of completed tasks.
*   **Worker:** A container running a Celery worker process that consumes tasks from RabbitMQ. (`worker` service in `docker-compose.yml`)
*   **Leek:** A web-based monitoring dashboard for Celery. (`leek` service in `docker-compose.yml`)
    *   Dashboard: http://localhost:5050

## Configuration

*   **Broker URL:** `amqp://guest:guest@rabbitmq:5672/` (Configured in `celery_app/celery_instance.py` and used by Leek)
*   **Result Backend URL:** `redis://redis:6379/0` (Configured in `celery_app/celery_instance.py` and used by Leek)
*   Service names (`rabbitmq`, `redis`) are used as hostnames within the Docker network.

## Shutting Down

To stop and remove the containers, network, and volumes:

```bash
docker compose down -v # The -v flag removes the named volumes (rabbitmq_data, redis_data)
```

---