# Task, Message Broker, and Monitoring system

This project demonstrates a Celery task queue setup with RabbitMQ as the message broker, Redis as the result backend, and Leek for monitoring, all orchestrated with Docker Compose.

## Architecture
```mermaid
graph TD
    subgraph "Docker Compose Services"
        RabbitMQ[(RabbitMQ <br> Message Broker <br> Port: 5672 - AMQP <br> Port: 15672 - Management)]
        Redis[(Redis <br> Result Backend <br> Port: 6379)]
        Worker[Celery Worker <br> Processes 3 queues: <br> default_queue,quick_task,long_task]
        Elasticsearch[(Elasticsearch <br> Stores Task History <br> Port: 9200)]
        
        subgraph "Leek Monitoring System"
            LeekAPI[Leek API <br> REST Interface <br> Port: 5000]
            LeekWeb[Leek Web UI <br> Task Dashboard <br> Port: 5001]
            LeekAgent[Leek Agent <br> Event Collector]
        end
    end
    
    Client[Web Client/User] -->|Access Dashboard| LeekWeb
    LeekWeb -->|Query Data| LeekAPI
    LeekAPI -->|Read Task History| Elasticsearch
    LeekAgent -->|Store Task Events| Elasticsearch
    LeekAgent -->|Subscribe to celeryev| RabbitMQ
    
    Worker -->|Consume Tasks| RabbitMQ
    Worker -->|Store Results| Redis
    Worker -->|Publish Task Events| RabbitMQ
```

## Prerequisites

* Docker ([Installation Guide](https://docs.docker.com/get-docker/))
* Docker Compose ([Installation Guide](https://docs.docker.com/compose/install/))

## Directory Structure

```
celery_kombu_docker_example/
├── docker-compose.yml        # Defines services (RabbitMQ, Redis, Celery, ElasticSearch, Leek)
├── celery_app/
│   ├── __init__.py
│   ├── celery_instance.py    # Celery App instance and configuration
│   ├── tasks.py              # Example Celery tasks
│   ├── run_sender.py         # Script to send example tasks
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Docker image for Celery worker
└── README.md                 # This file
```

## Components

* **Celery**: Distributed task queue system
* **RabbitMQ**: Message broker for Celery
* **Redis**: Result backend for Celery
* **ElasticSearch**: Database for Leek monitoring tool
* **Leek**: Celery monitoring dashboard

## Port Configuration

| Service | Container Port | Host Port | Description |
|---------|---------------|-----------|-------------|
| RabbitMQ | 5672 | 5672 | AMQP protocol |
| RabbitMQ | 15672 | 15672 | Management UI |
| Redis | 6379 | 6379 | Redis server |
| ElasticSearch | 9200 | 9200 | ElasticSearch API |
| Leek Web UI | 8000 | 5000 | Monitoring dashboard |
| Leek API | 5002 | 5002 | REST API |

## How to Run

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd celery_kombu_docker_example
    ```

2. **Build and start the services:**
    ```bash
    docker compose up --build -d
    ```

3. **Check service status:**
    ```bash
    docker compose ps
    ```

4. **Access the monitoring interfaces:**
   * RabbitMQ Management: http://localhost:15672 (user: guest, password: guest)
   * Leek Monitoring Dashboard: http://localhost:5000

## Celery Tasks

This example includes three sample tasks:

1. **add(x, y)**: A simple task that adds two numbers
2. **long_task(duration)**: A task that simulates long-running work by sleeping
3. **task_with_info(data)**: A task that prints information about its execution context

## Monitoring with Leek

Leek is a comprehensive Celery monitoring tool that provides:
* Task queue visualization
* Task execution details and history
* Performance metrics and issue tracking
* Multi-broker support

### Initial Setup

1. Access the Leek UI at http://localhost:5000
2. Create a new application named `celeryinstance`
3. After creation, you'll see tasks being monitored as they're executed

## Running Tasks

You can execute the example tasks using the provided script:

```bash
# Execute inside the worker container
docker compose exec worker python -m celery_app.run_sender

# Or directly on your host if Python and dependencies are installed
python -m celery_app.run_sender
```

## Configuration Details

### Celery Configuration

The Celery app is configured in `celery_instance.py` with:
* Broker URL: `amqp://guest:guest@rabbitmq:5672//`
* Result Backend: `redis://redis:6379/0`
* Task events enabled for monitoring
* JSON serialization for tasks and results
* Asia/Taipei timezone

### Leek Configuration

Leek is configured to:
* Connect to RabbitMQ to consume Celery events
* Use ElasticSearch for storing task data
* Provide a web UI for monitoring tasks
* Run with authentication disabled for this demo

## Shutting Down

To stop and remove all services:

```bash
docker compose down -v  # The -v flag removes volumes
```

## Troubleshooting

* **Port Conflicts**: If you encounter port conflicts, edit the port mappings in `docker-compose.yml`
* **Leek Connection Issues**: Ensure ElasticSearch is running and create the application in Leek UI
* **Task Visibility**: Make sure `task_send_sent_event` and `worker_send_task_events` are enabled in the Celery configuration

## Resources

* [Celery Documentation](https://docs.celeryq.dev/)
* [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
* [Redis Documentation](https://redis.io/documentation)
* [Leek Documentation](https://tryleek.com/docs/introduction/leek/)
