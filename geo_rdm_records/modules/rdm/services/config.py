# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services configuration."""

from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    PIDComponent,
    RelationsComponent,
)
from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.components import (
    AccessComponent,
    CustomFieldsComponent,
    MetadataComponent,
    PIDsComponent,
    ReviewComponent,
)
from invenio_records_resources.services.base.config import (
    FromConfig,
    FromConfigSearchOptions,
)
from invenio_records_resources.services.records.links import pagination_links

from geo_rdm_records.base.services.components import HarvesterComponent
from geo_rdm_records.base.services.config import (
    BaseGEOServiceConfig,
    GEOSearchDraftsOptions,
    GEOSearchOptions,
)
from geo_rdm_records.base.services.links import LinksRegistryType
from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy
from geo_rdm_records.base.services.results import MutableRecordList, ResultRegistryType
from geo_rdm_records.modules.marketplace.records.api import GEOMarketplaceItem
from geo_rdm_records.modules.rdm.services.schemas import (
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

    # Result classes
    result_list_cls = MutableRecordList
    results_registry_type = ResultRegistryType

    # Links
    links_registry_type = LinksRegistryType

    # Indices used to suggest related content
    indices_more_like_this = [
        GEORecord.index.search_alias,
        GEOMarketplaceItem.index.search_alias,
    ]

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_RDM_RECORDS_PERMISSION_POLICY",
        default=BaseGEOPermissionPolicy,
        import_string=True,
    )

    # Components - order matters!
    components = [
        ResourceRelationshipComponent,
        PackageResourceCommunitiesComponent,
        MetadataComponent,
        CustomFieldsComponent,
        AccessComponent,
        DraftFilesComponent,
        # for the internal `pid` field
        PIDComponent,
        # for the `pids` field (external PIDs)
        PIDsComponent,
        RelationsComponent,
        ReviewComponent,
        HarvesterComponent,
    ]

    #
    # Packages API extension
    #
    search_resource = FromConfigSearchOptions(
        "RDM_SEARCH_PACKAGE_RESOURCE",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=GEOSearchOptions,
    )

    search_resource_drafts = FromConfigSearchOptions(
        "RDM_SEARCH_PACKAGE_RESOURCE_DRAFTS",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=GEOSearchDraftsOptions,
    )

    links_search_package_records = pagination_links(
        "{+api}/packages/{id}/resources{?args*}"
    )

    links_search_package_drafts = pagination_links(
        "{+api}/packages/{id}/draft/resources{?args*}"
    )

    links_search_package_context = pagination_links(
        "{+api}/packages/context/{id}/resources{?args*}"
    )


class GEOFileRecordServiceConfig(rdm_config.RDMFileRecordServiceConfig):
    """Configuration for record files."""

    record_cls = GEORecord


class GEOFileDraftServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """Configuration for draft files."""

    record_cls = GEODraft
