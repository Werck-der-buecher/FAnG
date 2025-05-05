from decorators import check_docker_status
from services.settings import Settings
from .docker_image import DockerImage
from typing import List, Dict, Optional, Tuple, Any, Awaitable

import docker
import asyncio


class DockerService(object):
    """
    The class responsible to interact between the application and Docker APIs.
    """
    __slots__ = ['client', 'docker_image']

    client: docker.DockerClient
    docker_image: str

    @check_docker_status
    def __init__(self, config: Settings) -> None:
        self.client: docker.DockerClient = docker.from_env(timeout=None, max_pool_size=config.max_pool_size)
        self.docker_image: DockerImage = DockerImage(self.client)

    async def create_task(self, image_name: str, command: List[str], environment: Optional[Dict[str, str]],
                          working_dir: Optional[str], volumes: Optional[Dict[str, Dict[str, str]]]
                          ) -> Tuple[Any, Any]:
        """
        Create docker command and wrap it into an asynchronous coroutine.
        :param image_name:
        :param command:
        :param environment:
        :param working_dir:
        :param volumes:
        :return:
        """
        container = self.client.containers.run(image_name, command=command, environment=environment,
                                               working_dir=working_dir, volumes=volumes, detach=True)
        awaitable = asyncio.to_thread(container.wait)
        result = await awaitable
        logs = container.logs()
        container.remove()

        return result, logs

    async def exec_task(self, coroutine: Awaitable):
        """
        Execute concurrent coroutine
        :param coroutine:
        :return:
        """
        return asyncio.run(coroutine)

    @staticmethod
    def check_system_status() -> bool:
        """
        Check if Docker is correctly installed and whether the docker Daemon is running.
        :return: bool docker system status
        """
        try:
            client = docker.from_env()
            client.ping()
        except docker.errors.DockerException as e:
            return False
        else:
            return True
