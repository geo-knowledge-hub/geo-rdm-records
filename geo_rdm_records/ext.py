# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records extension definition."""

from invenio_rdm_records.services import SecretLinkService
from invenio_rdm_records.services.pids import PIDManager, PIDsService
from invenio_rdm_records.services.review.service import ReviewService
from invenio_records_resources.resources.files import FileResource
from invenio_records_resources.services import FileService

from . import config
from .modules.packages.resources.config import (
    GEOPackageDraftFilesResourceConfig,
    GEOPackageParentRecordLinksResourceConfig,
    GEOPackageRecordFilesResourceConfig,
    GEOPackageRecordResourceConfig,
)
from .modules.packages.resources.resource import (
    GEOPackageParentRecordLinksResource,
    GEOPackageRecordResource,
)
from .modules.packages.services.config import (
    GEOPackageDraftServiceConfig,
    GEOPackageFileRecordServiceConfig,
    GEOPackageRecordServiceConfig,
)
from .modules.packages.services.service import GEOPackageRecordService


class GEORDMRecords(object):
    """GEO Knowledge Hub Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # Packages API and Members API
        self.init_services(app)
        self.init_resource(app)

        app.extensions["geo-rdm-records"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Invenio RDM Records configuration
        supported_configurations = [
            "RDM_FACETS",
            "RDM_RECORD_SERVICE_CFG",
            "RDM_FILE_SERVICE_CFG",
            "RDM_FILE_DRAFT_SERVICE_CFG",
            "RDM_RECORD_RESOURCE_CFG",
            "RDM_FILE_RESOURCE_CFG",
            "RDM_FILE_DRAFT_RESOURCE_CFG",
            "RDM_PARENT_LINK_RESOURCE_CFG",
            "RDM_AFFILIATIONS_RESOURCE_CFG",
            "RDM_NAMES_RESOURCE_CFG",
            "RDM_SUBJECTS_RESOURCE_CFG",
        ]
        for k in dir(config):
            if k in supported_configurations or k.startswith("GEO_RDM_"):
                app.config.setdefault(k, getattr(config, k))

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            record = GEOPackageRecordServiceConfig.build(app)
            file = GEOPackageFileRecordServiceConfig.build(app)
            file_draft = GEOPackageDraftServiceConfig.build(app)

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
        )

    def init_resource(self, app):
        """Initialize resources."""
        self.package_records_resource = GEOPackageRecordResource(
            GEOPackageRecordResourceConfig,
            self.service,
        )

        # Record files resource
        self.package_record_files_resource = FileResource(
            service=self.service.files,
            config=GEOPackageRecordFilesResourceConfig,
        )

        # Draft files resource
        self.package_draft_files_resource = FileResource(
            service=self.service.draft_files,
            config=GEOPackageDraftFilesResourceConfig,
        )

        # Parent Records
        self.package_parent_record_links_resource = GEOPackageParentRecordLinksResource(
            service=self.service,
            config=GEOPackageParentRecordLinksResourceConfig,
        )
