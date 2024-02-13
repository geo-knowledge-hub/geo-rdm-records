# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Service config."""

from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    PIDComponent,
    RelationsComponent,
)
from invenio_drafts_resources.services.records.config import is_record
from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.components import (
    AccessComponent,
    CustomFieldsComponent,
    MetadataComponent,
    PIDsComponent,
    ReviewComponent,
)
from invenio_rdm_records.services.config import is_draft, is_draft_and_has_review
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.config import FromConfig

from geo_rdm_records.base.services.config import BaseGEOServiceConfig
from geo_rdm_records.base.services.links import LinksRegistryType
from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy
from geo_rdm_records.base.services.results import MutableRecordList, ResultRegistryType
from geo_rdm_records.base.services.schemas import ParentSchema
from geo_rdm_records.base.services.schemas.records import BaseGEORecordSchema
from geo_rdm_records.modules.marketplace.records.api import (
    GEOMarketplaceItem,
    GEOMarketplaceItemDraft,
)
from geo_rdm_records.modules.packages.services.links import RecordLink


class GEOMarketplaceServiceConfig(BaseGEOServiceConfig):
    """GEO Marketplace Item Service config."""

    # Record and draft classes
    record_cls = GEOMarketplaceItem
    draft_cls = GEOMarketplaceItemDraft

    # Schemas
    schema = BaseGEORecordSchema
    schema_parent = ParentSchema

    # Results
    result_list_cls = MutableRecordList
    results_registry_type = ResultRegistryType

    # Links
    links_registry_type = LinksRegistryType

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_MARKETPLACE_ITEMS_PERMISSION_POLICY",
        default=BaseGEOPermissionPolicy,  # ToDo: Review permissions for Marketplace
        import_string=True,
    )

    # Service components
    components = [
        MetadataComponent,
        CustomFieldsComponent,
        AccessComponent,
        DraftFilesComponent,
        # for the internal `pid` field
        PIDComponent,
        # for the `pids` field (external PIDs)
        # PIDsComponent,
        RelationsComponent,
        ReviewComponent,
    ]

    # Links
    # ToDo: Review links
    links_item = {
        "self": ConditionalLink(
            cond=is_record,
            # ToDo: Review this `RecordLink` (Generalize it?)
            if_=RecordLink("{+api}/marketplace/items/{id}"),
            else_=RecordLink("{+api}/marketplace/items/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/marketplace/items/{id}"),
            else_=RecordLink("{+ui}/uploads/marketplace/items/{id}"),
        ),
        # IIIF
        # ToDo: Review
        # "self_iiif_manifest": ConditionalLink(
        #     cond=is_record,
        #     if_=RecordLink("{+api}/iiif/marketplace/items:{id}/manifest"),
        #     else_=RecordLink("{+api}/iiif/package-draft:{id}/manifest"),
        # ),
        # "self_iiif_sequence": ConditionalLink(
        #     cond=is_record,
        #     if_=RecordLink("{+api}/iiif/package:{id}/sequence/default"),
        #     else_=RecordLink("{+api}/iiif/package-draft:{id}/sequence/default"),
        # ),
        # Files
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/marketplace/items/{id}/files"),
            else_=RecordLink("{+api}/marketplace/items/{id}/draft/files"),
        ),
        "files_import": RecordLink(
            "{+api}/marketplace/items/{id}/draft/actions/files-import", when=is_draft
        ),
        "latest": RecordLink(
            "{+api}/marketplace/items/{id}/versions/latest", when=is_record
        ),
        "latest_html": RecordLink(
            "{+ui}/marketplace/items/{id}/latest", when=is_record
        ),
        "draft": RecordLink("{+api}/marketplace/items/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/marketplace/items/{id}", when=is_draft),
        # TODO: record_html temporarily needed for DOI registration, until
        # problems with self_doi has been fixed
        # "record_html": RecordLink("{+ui}/marketplace/items/{id}", when=is_draft),
        "publish": RecordLink(
            "{+api}/marketplace/items/{id}/draft/actions/publish", when=is_draft
        ),
        "review": RecordLink(
            "{+api}/marketplace/items/{id}/draft/review", when=is_draft
        ),
        "submit-review": RecordLink(
            "{+api}/marketplace/items/{id}/draft/actions/submit-review",
            when=is_draft_and_has_review,
        ),
        "versions": RecordLink("{+api}/marketplace/items/{id}/versions"),
        "access_links": RecordLink("{+api}/marketplace/items/{id}/access/links"),
        # ToDo: Remove from the service method!
        # "reserve_doi": RecordLink("{+api}/packages/{id}/draft/pids/doi"),
    }


class GEOMarketplaceItemFileServiceConfig(rdm_config.RDMFileRecordServiceConfig):
    """GEO Marketplace Item file service config."""

    record_cls = GEOMarketplaceItem


class GEOMarketplaceItemDraftFileServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """GEO Marketplace Item (Draft) file service config."""

    record_cls = GEOMarketplaceItemDraft