# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services configuration."""

from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.customizations import FromConfigSearchOptions
from invenio_records_resources.services.records.links import pagination_links

from geo_rdm_records.modules.resources.records.api import GEODraft, GEORecord
from geo_rdm_records.modules.resources.services.components import (
    PackageResourceCommunitiesComponent,
    ResourceRelationshipComponent,
)
from geo_rdm_records.modules.resources.services.params.search import BoundingBoxParam
from geo_rdm_records.modules.resources.services.schemas import (
    GEOParentSchema,
    GEORecordSchema,
)


class GEOSearchOptions(rdm_config.RDMSearchOptions):
    """Search options for record search."""

    params_interpreters_cls = rdm_config.RDMSearchOptions.params_interpreters_cls + [
        BoundingBoxParam.factory("metadata.locations.features.geometry")
    ]


class GEOSearchDraftsOptions(rdm_config.RDMSearchDraftsOptions):
    """Search options for record search."""

    params_interpreters_cls = (
        rdm_config.RDMSearchDraftsOptions.params_interpreters_cls
        + [BoundingBoxParam.factory("metadata.locations.features.geometry")]
    )


class GEOSearchVersionsOptions(rdm_config.RDMSearchVersionsOptions):
    """Search options for record versioning search."""

    params_interpreters_cls = (
        rdm_config.RDMSearchVersionsOptions.params_interpreters_cls
        + [BoundingBoxParam.factory("metadata.locations.features.geometry")]
    )


class GEORecordServiceConfig(rdm_config.RDMRecordServiceConfig):
    """GEO record draft service config."""

    # Record and draft classes
    record_cls = GEORecord
    draft_cls = GEODraft

    # Schemas
    schema = GEORecordSchema
    schema_parent = GEOParentSchema

    # Search configuration
    search = FromConfigSearchOptions("RDM_SEARCH", search_option_cls=GEOSearchOptions)
    search_drafts = FromConfigSearchOptions(
        "RDM_SEARCH_DRAFTS", search_option_cls=GEOSearchDraftsOptions
    )
    search_versions = FromConfigSearchOptions(
        "RDM_SEARCH_VERSIONING", search_option_cls=GEOSearchVersionsOptions
    )

    # Components - order matters!
    components = [
        ResourceRelationshipComponent,
        PackageResourceCommunitiesComponent,
    ] + rdm_config.RDMRecordServiceConfig.components

    #
    # Packages API extension
    #
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
