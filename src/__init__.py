"""Service for monitoring exchange rates and serve

Requirement service:
    * RabbitMQ

Typical usage algorithm:
    1. Define environment variables using dotenv or system methods
    2. Startup exchange rate monitor
        `python -m src.modules.exchange_monitor.app`
    3. Startup API
        `uvicorn src.modules.api.app:app`
"""
