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
    ReviewComponent,
)
from invenio_rdm_records.services.config import (
    is_draft,
    is_draft_and_has_review,
    is_iiif_compatible,
)
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.config import FromConfig
from invenio_records_resources.services.files.links import FileLink
from invenio_records_resources.services.records.links import RecordLink

from geo_rdm_records.base.services.config import BaseGEOServiceConfig
from geo_rdm_records.base.services.links import LinksRegistryType
from geo_rdm_records.base.services.schemas import ParentSchema
from geo_rdm_records.base.services.schemas.records import BaseGEORecordSchema
from geo_rdm_records.modules.marketplace.records.api import (
    GEOMarketplaceItem,
    GEOMarketplaceItemDraft,
)
from geo_rdm_records.modules.marketplace.services.permissions import (
    MarketplacePermissionPolicy,
)
from geo_rdm_records.modules.packages.records.api import GEOPackageRecord


class GEOMarketplaceServiceConfig(BaseGEOServiceConfig):
    """GEO Marketplace Item Service config."""

    # Record and draft classes
    record_cls = GEOMarketplaceItem
    draft_cls = GEOMarketplaceItemDraft

    # Schemas
    schema = BaseGEORecordSchema
    schema_parent = ParentSchema

    # Links
    links_registry_type = LinksRegistryType

    # Indices used to suggest related content
    indices_more_like_this = [
        GEOPackageRecord.index.search_alias,
        GEOMarketplaceItem.index.search_alias,
    ]

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_MARKETPLACE_ITEMS_PERMISSION_POLICY",
        default=MarketplacePermissionPolicy,  # ToDo: Review permissions for Marketplace
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
        "self_iiif_manifest": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/iiif/marketplace-item:{id}/manifest"),
            else_=RecordLink("{+api}/iiif/marketplace-item-draft:{id}/manifest"),
        ),
        "self_iiif_sequence": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/iiif/marketplace-item:{id}/sequence/default"),
            else_=RecordLink(
                "{+api}/iiif/marketplace-item-draft:{id}/sequence/default"
            ),
        ),
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
        "record_html": RecordLink("{+ui}/marketplace/items/{id}", when=is_draft),
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

    # Configurations
    service_id = "files_marketplace"

    # Record class
    record_cls = GEOMarketplaceItem

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_MARKETPLACE_ITEMS_PERMISSION_POLICY",
        default=MarketplacePermissionPolicy,  # ToDo: Review permissions for Marketplace
        import_string=True,
    )

    file_links_item = {
        "self": FileLink("{+api}/marketplace/items/{id}/files/{key}"),
        "content": FileLink("{+api}/marketplace/items/{id}/files/{key}/content"),
        # FIXME: filename instead
        "iiif_canvas": FileLink(
            "{+api}/iiif/marketplace-item:{id}/canvas/{key}", when=is_iiif_compatible
        ),
        "iiif_base": FileLink(
            "{+api}/iiif/marketplace-item:{id}:{key}", when=is_iiif_compatible
        ),
        "iiif_info": FileLink(
            "{+api}/iiif/marketplace-item:{id}:{key}/info.json", when=is_iiif_compatible
        ),
        "iiif_api": FileLink(
            "{+api}/iiif/marketplace-item:{id}:{key}/{region=full}"
            "/{size=full}/{rotation=0}/{quality=default}.{format=png}",
            when=is_iiif_compatible,
        ),
    }


class GEOMarketplaceItemDraftFileServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """GEO Marketplace Item (Draft) file service config."""

    # Configurations
    service_id = "files_marketplace_draft"

    # Record class
    record_cls = GEOMarketplaceItemDraft

    # Permission policy
    permission_action_prefix = "draft_"
    permission_policy_cls = FromConfig(
        "GEO_MARKETPLACE_ITEMS_PERMISSION_POLICY",
        default=MarketplacePermissionPolicy,  # ToDo: Review permissions for Marketplace
        import_string=True,
    )

    file_links_list = {
        "self": RecordLink("{+api}/marketplace/items/{id}/draft/files"),
    }

    file_links_item = {
        "self": FileLink("{+api}/marketplace/items/{id}/draft/files/{key}"),
        "content": FileLink("{+api}/marketplace/items/{id}/draft/files/{key}/content"),
        "commit": FileLink("{+api}/marketplace/items/{id}/draft/files/{key}/commit"),
        # FIXME: filename instead
        "iiif_canvas": FileLink(
            "{+api}/iiif/marketplace-item-draft:{id}/canvas/{key}",
            when=is_iiif_compatible,
        ),
        "iiif_base": FileLink(
            "{+api}/iiif/marketplace-item-draft:{id}:{key}", when=is_iiif_compatible
        ),
        "iiif_info": FileLink(
            "{+api}/iiif/marketplace-item-draft:{id}:{key}/info.json",
            when=is_iiif_compatible,
        ),
        "iiif_api": FileLink(
            "{+api}/iiif/marketplace-item-draft:{id}:{key}/{region=full}"
            "/{size=full}/{rotation=0}/{quality=default}.{format=png}",
            when=is_iiif_compatible,
        ),
    }
