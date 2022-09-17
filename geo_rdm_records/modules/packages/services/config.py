# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Service configuration."""

from invenio_drafts_resources.services.records.config import is_record
from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.customizations import FromConfig
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.records.links import RecordLink

from geo_rdm_records.base.services.config import BaseGEOServiceConfig
from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy
from geo_rdm_records.customizations.records.api import GEODraft, GEORecord

from ..records.api import GEOPackageDraft, GEOPackageRecord
from .components.relationship import PackageRelationshipComponent
from .components.resources import (
    PackageResourceAccessComponent,
    PackageResourceCommunityComponent,
    PackageResourceIntegrationComponent,
)
from .schemas import GEOPackageRecordSchema


class GEOPackageRecordServiceConfig(BaseGEOServiceConfig):
    """GEO Package record draft service config."""

    # Configurations
    service_id = "records_package"

    # Record and draft classes
    record_cls = GEOPackageRecord
    draft_cls = GEOPackageDraft

    # Configuring the resources classes
    resource_cls = GEORecord
    resource_draft_cls = GEODraft

    # Schemas
    schema = GEOPackageRecordSchema

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=BaseGEOPermissionPolicy,
        import_string=True,
    )

    # Service components
    components = [
        PackageRelationshipComponent,
        PackageResourceIntegrationComponent,
        PackageResourceAccessComponent,
        PackageResourceCommunityComponent,
    ] + rdm_config.RDMRecordServiceConfig.components

    # Links
    links_item = {
        **rdm_config.RDMRecordServiceConfig.links_item,
        "resources": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/packages/{id}/resources"),
            else_=RecordLink("{+api}/packages/{id}/draft/resources"),
        ),
    }


class GEOPackageFileRecordServiceConfig(rdm_config.RDMFileRecordServiceConfig):
    """Configuration for package files."""

    # Configurations
    service_id = "files_package"

    # Record class
    record_cls = GEOPackageRecord

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=BaseGEOPermissionPolicy,
        import_string=True,
    )


class GEOPackageDraftServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """Configuration for draft files."""

    # Configurations
    service_id = "files_package_draft"

    # Record class
    record_cls = GEOPackageDraft

    # Permission policy
    permission_action_prefix = "draft_"
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=BaseGEOPermissionPolicy,
        import_string=True,
    )
