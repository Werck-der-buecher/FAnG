from requests.exceptions import ConnectionError as RequestsConnectionError
from services.docker_service.docker_errors import DockerDaemonConnectionError

import os


def check_docker_status(method):
    """
    Decorator function to check if Docker daemon is running properly.
    See https://github.com/KatharaFramework/Kathara/blob/fa03cea989d6be8ebdad179cb90cb2fc1b012787/src/Kathara/manager/docker/DockerManager.py
    """

    def check_docker(*args, **kw):
        # Call the constructor first
        method(*args, **kw)

        # Client is initialized after constructor call
        client = args[0].client

        # Try to ping Docker, to see if it's running and raise an exception on failure
        try:
            client.ping()
        except RequestsConnectionError as e:
            raise DockerDaemonConnectionError(f"Can not connect to Docker Daemon. {str(e)}")

    return check_docker


def async_check_docker_status(method):
    """
    Decorator function to check if Docker daemon is running properly.
    See https://github.com/KatharaFramework/Kathara/blob/fa03cea989d6be8ebdad179cb90cb2fc1b012787/src/Kathara/manager/docker/DockerManager.py
    """
    def check_docker(*args, **kw):
        # Call the constructor first
        method(*args, **kw)

        # Client is initialized after constructor call
        client = args[0].client

        # Try to ping Docker, to see if it's running and raise an exception on failure
        try:
            if "DOCKER_HOST" in os.environ:
                if (
                        os.environ["DOCKER_HOST"].startswith("http://")
                        or os.environ["DOCKER_HOST"].startswith("https://")
                        or os.environ["DOCKER_HOST"].startswith("tcp://")
                ):
                    assert client.docker_host == os.environ["DOCKER_HOST"]
                else:
                    assert client.docker_host in ["unix://localhost", "npipe://localhost"]
            else:
                # assuming that docker daemon is installed locally.
                assert client.docker_host is not None
        except AssertionError as e:
            raise DockerDaemonConnectionError(f"Can not connect to Docker Daemon. {str(e)}")

    return check_docker