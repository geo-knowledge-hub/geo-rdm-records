# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services configuration."""

from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.customizations import (
    FromConfig,
    FromConfigSearchOptions,
)
from invenio_records_resources.services.records.links import pagination_links

from geo_rdm_records.base.services.config import (
    BaseGEOServiceConfig,
    GEOSearchDraftsOptions,
    GEOSearchOptions,
)
from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy
from geo_rdm_records.customizations.services.schemas import (
    GEOParentSchema,
    GEORecordSchema,
)

from ..records.api import GEODraft, GEORecord
from .components import (
    PackageResourceCommunitiesComponent,
    ResourceRelationshipComponent,
)


class GEORecordServiceConfig(BaseGEOServiceConfig):
    """GEO record draft service config."""

    # Record and draft classes
    record_cls = GEORecord
    draft_cls = GEODraft

    # Schemas
    schema = GEORecordSchema
    schema_parent = GEOParentSchema

    # Permission policy
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=BaseGEOPermissionPolicy, import_string=True
    )

    # Components - order matters!
    components = [
        ResourceRelationshipComponent,
        PackageResourceCommunitiesComponent,
    ] + rdm_config.RDMRecordServiceConfig.components

    #
    # Packages API extension
    #
    search_resource = FromConfigSearchOptions(
        "RDM_SEARCH_PACKAGE_RESOURCE", search_option_cls=GEOSearchOptions
    )

    search_resource_drafts = FromConfigSearchOptions(
        "RDM_SEARCH_PACKAGE_RESOURCE_DRAFTS", search_option_cls=GEOSearchDraftsOptions
    )

    links_search_package_records = pagination_links(
        "{+api}/packages/{id}/resources{?args*}"
    )

    links_search_package_drafts = pagination_links(
        "{+api}/packages/{id}/draft/resources{?args*}"
    )


class GEOFileRecordServiceConfig(rdm_config.RDMFileRecordServiceConfig):
    """Configuration for record files."""

    record_cls = GEORecord


class GEOFileDraftServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """Configuration for draft files."""

    record_cls = GEODraft
