from decorators import async_check_docker_status
from .docker_image import AsyncDockerImage
from typing import Dict, Any, Optional

import logging
import os
import asyncio
from aiodocker.docker import Docker
from aiodocker.exceptions import DockerError
from services.settings import Settings


class AsyncDockerService(object):
    """
    The class responsible to interact between the application and Docker APIs.
    """
    def __init__(self, config: Settings) -> None:
        self.config: Settings = config
        self.client: Optional[Docker, None] = None
        self.docker_image: Optional[AsyncDockerImage, None] = None

    @async_check_docker_status
    def setup_service(self):
        self.client = Docker()
        self.docker_image = AsyncDockerImage(self.client)

    async def close(self) -> None:
        await self.client.close()

    async def exec_command(self, config: Dict[str, Any], logging_level: int = logging.INFO):
        """
        Asynchronous invocation of Docker container that executes given command.
        :param config:
        :param logging_level:
        :return:
        """
        image_name = config.get('Image')
        try:
            await self.client.images.inspect(image_name)
        except DockerError as e:
            logging.log(logging_level, f"Error retrieving Docker image '{image_name}'. Setup phase for the application went wrong.")
            return

        logging.log(logging_level, f"Running Docker container according to specified config with Docker image '{image_name}'")

        # setup aiohttp event listener to retrieve and handle docker events
        event_listener = self.client.events.subscribe()

        # start (and potentially recreate) Docker container
        msg_prefix = ">>> DOCKER CONTAINER EVENT"
        container = await self.client.containers.create_or_replace(config=config, name=config['name'])
        await container.start()
        logging.log(logging_level, f"{msg_prefix} - Created and started container {container._id[:12]}")

        while True:
            event = await event_listener.get()
            if event is None:
                logging.log(logging_level, f"{msg_prefix} - No event received... breaking.")
                break
            if event["Actor"]["ID"] == container._id:
                if event["Action"] == "start":
                    async for chunk in container.log(follow=True, stdout=True, stderr=True):
                        logging.log(logging_level, chunk)
                    await container.stop()
                    logging.log(logging_level, f"{msg_prefix} - Stopped/killed {container._id[:12]}")
                elif event["Action"] == "stop":
                    await container.delete(force=True)
                    logging.log(logging_level, f"{msg_prefix} - Deleted {container._id[:12]}")
                elif event["Action"] == "die":
                    await container.delete(force=True)
                    logging.log(logging_level, f"{msg_prefix} - Died {container._id[:12]}")
                elif event["Action"] == "destroy":
                    logging.log(logging_level, f"{msg_prefix} - Container successfully destroyed.")
                    break

    @staticmethod
    def check_system_status() -> bool:
        """
        Check if Docker is correctly installed and whether the docker Daemon is running.
        :return: bool docker system status
        """
        try:
            client = Docker()
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
            loop = asyncio.get_event_loop()
            loop.create_task(client.close())
        except (ValueError, AssertionError) as e:
            return False
        else:
            return True
