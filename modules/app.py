from injector import Module, provider, singleton, inject
from services import Settings, Settings, DockerService, AsyncDockerService, GlyphClassifierService, LoggingService, GSQLService


class AppModule(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return Settings.get_instance()

    @inject
    @provider
    def provide_gsql(self, settings: Settings) -> GSQLService:
        return GSQLService(settings)

    @inject
    @singleton
    @provider
    def provide_logger(self, settings: Settings) -> LoggingService:
        return LoggingService(settings)

    @inject
    @singleton
    @provider
    def provide_docker(self, settings: Settings) -> DockerService:
        return DockerService(settings)

    @inject
    @singleton
    @provider
    def provide_async_docker(self, settings: Settings) -> AsyncDockerService:
        return AsyncDockerService(settings)

    @inject
    @singleton
    @provider
    def provide_glyph_classifier(self, settings: Settings) -> GlyphClassifierService:
        return GlyphClassifierService(settings)
