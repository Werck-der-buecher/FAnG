import logging
from typing import Union, List, Set

import docker.models.images
from docker import DockerClient
from docker.errors import APIError

from services.docker_service.docker_errors import DockerImageNotFoundError

from pathlib import Path


class DockerImage(object):
    """
    Class responsible for interacting with Docker Images.
    See https://github.com/KatharaFramework/Kathara
    """
    __slots__ = ['client']

    def __init__(self, client: DockerClient) -> None:
        self.client: DockerClient = client

    def get_local(self, image_name: str) -> docker.models.images.Image:
        """Return the specified Docker Image.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            docker.models.images.Image: A Docker Image
        """
        return self.client.images.get(image_name)

    async def get_remote(self, image_name: str) -> docker.models.images.RegistryData:
        """Gets the registry data for an image.

        Args:
            image_name (str): The name of the image.

        Returns:
            docker.models.images.RegistryData: The data object.

        Raises:
            `docker_service.errors.APIError`: If the server returns an error.
        """
        return self.client.images.get_registry_data(image_name)

    async def pull(self, image_name: str) -> docker.models.images.Image:
        """Pull and return the specified Docker Image.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            docker.models.images.Image: A Docker Image
        """
        # If no tag or sha key is specified, we add "latest"
        if (':' or '@') not in image_name:
            image_name = "%s:latest" % image_name

        logging.info(f"Pulling image `{image_name}`... This may take a while.")
        image = self.client.images.pull(image_name)
        return image

    def load(self, image_name: str, docker_image_dir: Union[Path, str]):
        """ Load and return specific Docker Image from local path.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            docker.models.images.Image: A Docker Image
        """
        logging.info(f"Loading image `{image_name}` from exported file... This may take a while.")
        with open(str(Path(docker_image_dir).joinpath(image_name).absolute()) + ".tar", "rb") as f:
            self.client.images.setup_and_connect(f)
        return self.client.images.setup_and_connect(image_name)

    def check_for_updates(self, image_name: str) -> bool:
        """Update the specified image.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            None
        """
        logging.debug("Checking updates for %s..." % image_name)

        if '@' in image_name:
            logging.debug('No need to check image digest of {image_name}')
            return False

        local_image_info = self.get_local(image_name)
        # Image has been built locally, so there's nothing to compare.
        local_repo_digests = local_image_info.attrs["RepoDigests"]
        if not local_repo_digests:
            logging.debug(f"Image {image_name} is build locally")
            return False

        remote_image_info = self.get_remote(image_name).attrs['Descriptor']
        local_repo_digest = local_repo_digests[0]
        remote_image_digest = remote_image_info["digest"]

        # Format is image_name@sha256, so we strip the first part.
        (_, local_image_digest) = local_repo_digest.split("@")
        # We only need to update tagged images, not the ones with digests.
        return remote_image_digest != local_image_digest

    def check(self, image_name: str) -> None:
        """Check the existence of the specified image.

        Args:
            image_name (str): The name of a Docker Image.

        Returns:
            None

        Raises:
            ConnectionError: If there is a connection error while pulling the Docker image from Docker Hub.
            DockerImageNotFoundError: If the Docker image is not available neither on Docker Hub nor in local repository.
        """
        self.check_and_pull(image_name, pull=False)

    def check_from_list(self, images: Union[List[str], Set[str]]) -> None:
        """Check a list of specified images.

        Args:
            images (Union[List[str], Set[str]]): A list of Docker images name to pull.

        Returns:
            None
        """
        for image in images:
            self.check_and_pull(image)

    async def check_and_pull(self, image_name: str, pull: bool = True) -> None:
        """Check and pull of the specified image.

        Args:
            image_name (str): The name of a Docker Image.
            pull (bool): If True, pull the image from Docker Hub.

        Returns:
            None

        Raises:
            ConnectionError: If there is a connection error while pulling the Docker image from Docker Hub.
            DockerImageNotFoundError: If the Docker image is not available neither on Docker Hub
                nor in local repository.
        """
        try:
            # Tries to get the image from the local Docker repository.
            image = self.get_local(image_name)
            try:
                if pull:
                    self.check_for_updates(image_name)
            except APIError:
                logging.debug("Cannot check updates, skipping...")

        except APIError:
            # If not found, tries on Docker Hub.
            try:
                # If the image exists on Docker Hub, pulls it.
                registry_data = self.get_remote(image_name)
                if pull:
                    # If no tag or sha key is specified, we add "latest"
                    if (':' or '@') not in image_name:
                        image_name = "%s:latest" % image_name

                    logging.info(f"Pulling image `{image_name}`... This may take a while.")
                    return await self.client.images.pull(image_name)
            except APIError as e:
                if e.response.status_code == 500 and 'dial tcp' in e.explanation:
                    raise ConnectionError(
                        f"Docker Image `{image_name}` is not available in local repository and "
                        "no Internet connection is available to pull it from Docker Hub."
                    )
                else:
                    raise DockerImageNotFoundError(image_name)
