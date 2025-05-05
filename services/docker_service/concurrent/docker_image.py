import logging

# Async Docker Management
import asyncio
from aiodocker.docker import Docker
from aiodocker.exceptions import DockerError

from typing import Coroutine, Any, Mapping, Optional, Union, Generator, AsyncGenerator
from pathlib import Path


class AsyncDockerImage(object):
    """
    Class responsible for interacting with Docker Images supporting concurrent calls.
    """
    __slots__ = ['client']

    def __init__(self, client: Docker) -> None:
        self.client: Docker = client

    async def get_local(self, image_name: str) -> Coroutine[Any, Any, Mapping]:
        """Return the specified Docker Image.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            Coroutine[Any, Any, Mapping]
        """
        return await self.client.images.inspect(image_name)

    async def pull(self, image_name: str, tag: Optional[str] = 'latest') -> Any:
        """Pull and return the specified Docker Image.

        Args:
            image_name (str): The name of a Docker Image.
            tag (str): The tag of the Docker image. If empty, pulls all tag versions.
            
        Returns:
            docker.models.images.Image: A Docker Image
        """
        # If no tag or sha key is specified, we add "latest"
        if (':' or '@') not in image_name:
            tag = "latest"
        elif ':' in image_name:
            image_name, tag = image_name.split(':')
        elif '@' in image_name:
            image_name, tag = image_name.split('@')

        logging.info(f"Pulling image '{image_name}' with tag '{tag}'... This may take a while.")
        pull_result = await self.client.pull(image_name, tag=tag)
        return pull_result

    async def load(self, image_name: str, docker_image_dir: Union[Path, str]) -> Union[
        AsyncGenerator[Generator, Any], Coroutine[Any, Any, list[Generator]]]:
        """ Load and return specific Docker Image from local path.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            docker.models.images.Image: A Docker Image
        """
        logging.info(f"Loading image `{image_name}` from exported file... This may take a while.")
        with open(str(Path(docker_image_dir).joinpath(image_name).absolute()) + ".tar", "rb") as f:
            await self.client.images.import_image(image_name)
        return await self.client.images.inspect(image_name)
