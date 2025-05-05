class DockerDaemonConnectionError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Cannot connect to Docker Daemon: {message}")


class DockerImageNotFoundError(Exception):
    def __init__(self, image_name: str) -> None:
        super().__init__(
            f"Docker Image `{image_name}` is not available neither on Docker Hub nor in local repository!")
