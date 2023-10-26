"""Configs for Locust loading tests

Typical usage command (shell):
    locust --host 127.0.0.1

    # Or with set env:
    APP_URI=http://127.0.0.1:8000 locust --host 127.0.0.1
"""
import os

from locust import HttpUser, task, between


class CourseTestUser(HttpUser):
    """Loading test for Exchange Rates"""

    wait_time = between(0, 0)
    _host_uri: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        host_uri = os.getenv("APP_URI", None)

        if host_uri is None:
            raise EnvironmentError("you must setup target uri (APP_URI)")

        self._host_uri = host_uri

    @task(1)
    def get_courses(self):
        self.client.get(self._host_uri + "/courses")
