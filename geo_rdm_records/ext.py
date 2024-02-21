# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records extension definition."""

from invenio_rdm_records.services.pids import PIDManager, PIDsService
from invenio_rdm_records.services.review.service import ReviewService
from invenio_records_resources.resources.files import FileResource
from invenio_records_resources.services import FileService

from . import config
from .modules.marketplace.resources.config import (
    GEOMarketplaceItemDraftResourceConfig,
    GEOMarketplaceItemFilesResourceConfig,
    GEOMarketplaceItemResourceConfig,
)
from .modules.marketplace.resources.resource import GEOMarketplaceItemResource
from .modules.marketplace.services.config import (
    GEOMarketplaceItemDraftFileServiceConfig,
    GEOMarketplaceItemFileServiceConfig,
    GEOMarketplaceServiceConfig,
)
from .modules.marketplace.services.service import GEOMarketplaceItemService
from .modules.packages.resources.config import (
    GEOPackageDraftFilesResourceConfig,
    GEOPackageParentRecordLinksResourceConfig,
    GEOPackageParentRelationshipConfig,
    GEOPackageRecordFilesResourceConfig,
    GEOPackageRecordResourceConfig,
)
from .modules.packages.resources.resource import (
    GEOPackageContextResource,
    GEOPackageParentRecordLinksResource,
    GEOPackageRecordResource,
)
from .modules.packages.services.config import (
    GEOPackageDraftFileServiceConfig,
    GEOPackageFileRecordServiceConfig,
    GEOPackageRecordServiceConfig,
    GEOPackageRequestServiceConfig,
)
from .modules.packages.services.request.service import PackageRequestsService
from .modules.packages.services.secret_links import SecretLinkService
from .modules.packages.services.service import GEOPackageRecordService
from .modules.requests.services.config import RequestNotificationServiceConfig
from .modules.requests.services.service import RequestNotificationService
from .modules.search.resources.config import SearchRecordResourceConfig
from .modules.search.resources.resource import SearchRecordResource
from .modules.search.services.config import SearchRecordServiceConfig
from .modules.search.services.service import SearchRecordService


class GEORDMRecords(object):
    """GEO Knowledge Hub Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # Packages API
        self.init_services(app)
        self.init_resource(app)

        app.extensions["geo-rdm-records"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Invenio RDM Records configuration
        for k in dir(config):
            if k.startswith("RDM_") or k.startswith("GEO_RDM_"):
                app.config.setdefault(k, getattr(config, k))

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            # Package-related configurations
            record = GEOPackageRecordServiceConfig.build(app)
            file = GEOPackageFileRecordServiceConfig.build(app)
            file_draft = GEOPackageDraftFileServiceConfig.build(app)
            search = SearchRecordServiceConfig.build(app)
            requests = GEOPackageRequestServiceConfig.build(app)
            assistance_requests = RequestNotificationServiceConfig.build(app)

            # Marketplace-related configurations
            marketplace_item = GEOMarketplaceServiceConfig.build(app)
            marketplace_file = GEOMarketplaceItemFileServiceConfig.build(app)
            marketplace_file_draft = GEOMarketplaceItemDraftFileServiceConfig.build(app)

        return ServiceConfigs

    def init_services(self, app):
        """Initialize services."""
        service_configs = self.service_configs(app)

        # Services
        self.service = GEOPackageRecordService(
            service_configs.record,
            files_service=FileService(service_configs.file),
            draft_files_service=FileService(service_configs.file_draft),
            secret_links_service=SecretLinkService(service_configs.record),
            pids_service=PIDsService(
                service_configs.record, PIDManager
            ),  # same used for the records.
            review_service=ReviewService(service_configs.record),
            request_service=PackageRequestsService(service_configs.requests),
        )

        # Search service (Packages and records)
        self.service_search = SearchRecordService(config=service_configs.search)

        # Assistance requests service
        self.service_requests_notification = RequestNotificationService(
            config=service_configs.assistance_requests
        )

        # Marketplace item
        self.service_marketplace = GEOMarketplaceItemService(
            config=service_configs.marketplace_item,
            files_service=FileService(service_configs.marketplace_file),
            draft_files_service=FileService(service_configs.marketplace_file_draft),
        )

    def init_resource(self, app):
        """Initialize resources."""
        self.package_records_resource = GEOPackageRecordResource(
            GEOPackageRecordResourceConfig.build(app),
            self.service,
        )

        # Record files resource
        self.package_record_files_resource = FileResource(
            service=self.service.files,
            config=GEOPackageRecordFilesResourceConfig.build(app),
        )

        # Draft files resource
        self.package_draft_files_resource = FileResource(
            service=self.service.draft_files,
            config=GEOPackageDraftFilesResourceConfig.build(app),
        )

        # Parent Records
        self.package_parent_record_links_resource = GEOPackageParentRecordLinksResource(
            service=self.service,
            config=GEOPackageParentRecordLinksResourceConfig.build(app),
        )

        # Search
        self.search_resource = SearchRecordResource(
            service=self.service_search, config=SearchRecordResourceConfig.build(app)
        )

        # Context
        self.packages_context_resource = GEOPackageContextResource(
            service=self.service, config=GEOPackageParentRelationshipConfig
        )

        # Marketplace
        self.marketplace_resource = GEOMarketplaceItemResource(
            service=self.service_marketplace,
            config=GEOMarketplaceItemResourceConfig.build(app),
        )

        # Marketplace - Files
        self.marketplace_files_resource = FileResource(
            service=self.service_marketplace.files,
            config=GEOMarketplaceItemFilesResourceConfig.build(app),
        )

        # Marketplace - Draft files
        self.marketplace_draft_files_resource = FileResource(
            service=self.service_marketplace.draft_files,
            config=GEOMarketplaceItemDraftResourceConfig.build(app),
        )
