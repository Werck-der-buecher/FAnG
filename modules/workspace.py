from injector import Module, provider, singleton, inject, Binder, SingletonScope

from services import Settings, Settings, SimilarityCalculationService, WorkspacePersistenceService, GSQLService, \
    WorkspaceCacheService, WorkspaceBookmarkService


class WorkspaceModule(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return Settings.get_instance()

    @singleton
    @provider
    def provide_similarity_calculator(self) -> SimilarityCalculationService:
        return SimilarityCalculationService()

    @singleton
    @provider
    def provide_workspace_bookmarks(self) -> WorkspaceBookmarkService:
        return WorkspaceBookmarkService()

    @inject
    @provider
    def provide_gsql(self, settings: Settings) -> GSQLService:
        return GSQLService(settings)

    @inject
    @singleton
    @provider
    def provide_workspace_cache(self, gsql: GSQLService) -> WorkspaceCacheService:
        return WorkspaceCacheService(gsql)

    @inject
    @singleton
    @provider
    def provive_workspace_persistence(self,
                                      gsql: GSQLService,
                                      cache: WorkspaceCacheService,
                                      bookmarks: WorkspaceBookmarkService
                                      ) -> WorkspacePersistenceService:
        return WorkspacePersistenceService(gsql, cache, bookmarks)
