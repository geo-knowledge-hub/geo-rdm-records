# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Items API."""

from invenio_communities.records.records.systemfields import CommunitiesField
from invenio_drafts_resources.records import Draft, Record
from invenio_rdm_records.records.api import CommonFieldsMixin as BaseCommonFieldsMixin
from invenio_rdm_records.records.api import RDMParent as BaseRecordParent
from invenio_rdm_records.records.systemfields import (
    HasDraftCheckField,
    RecordAccessField,
)
from invenio_rdm_records.records.systemfields.draft_status import DraftStatus
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import FilesField, IndexField

from geo_rdm_records.base.records.api import GEOBaseRecord
from geo_rdm_records.base.records.categories import GEORecordCategories
from geo_rdm_records.base.records.systemfields.common import BaseGEORecordsFieldsMixin
from geo_rdm_records.base.records.types import GEORecordTypes

from .models import (
    GEOMarketplaceItemDraftFileMetadata,
    GEOMarketplaceItemDraftMetadata,
    GEOMarketplaceItemFileMetadata,
    GEOMarketplaceItemMetadata,
    GEOMarketplaceItemParentCommunityMetadata,
    GEOMarketplaceItemParentMetadata,
    GEOMarketplaceItemVersionsState,
)


#
# Parent
#
class GEOMarketplaceItemParent(GEOBaseRecord, BaseRecordParent):
    """Parent record."""

    # Configuration
    model_cls = GEOMarketplaceItemParentMetadata

    schema = ConstantField("$schema", "local://records/geo-parent-v1.0.0.json")

    communities = CommunitiesField(GEOMarketplaceItemParentCommunityMetadata)

    type = ConstantField("type", GEORecordTypes.marketplace_item)

    category = ConstantField("category", GEORecordCategories.marketplace)


#
# Record and Draft APIs.
#
class CommonFieldsMixin(BaseGEORecordsFieldsMixin, BaseCommonFieldsMixin):
    """Common system fields between published and draft packages."""

    versions_model_cls = GEOMarketplaceItemVersionsState
    parent_record_cls = GEOMarketplaceItemParent

    access = RecordAccessField()

    schema = ConstantField(
        "$schema",
        "local://marketplaceitems/marketplaceitems-records-record-v1.0.0.json",
    )


#
# Draft API.
#
class GEOMarketplaceItemDraftFile(FileRecord):
    """Record (Draft) File abstraction class."""

    model_cls = GEOMarketplaceItemDraftFileMetadata
    records_cls = None


class GEOMarketplaceItemDraft(CommonFieldsMixin, Draft):
    """Record (Draft) Metadata manipulation class API."""

    model_cls = GEOMarketplaceItemDraftMetadata

    index = IndexField(
        "marketplaceitems-drafts-draft-v1.0.0", search_alias="marketplaceitems"
    )

    files = FilesField(
        store=False,
        file_cls=GEOMarketplaceItemDraftFile,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()

    status = DraftStatus()


#
# Record API
#
class GEOMarketplaceItemFile(FileRecord):
    """Record File abstraction class."""

    model_cls = GEOMarketplaceItemFileMetadata
    records_cls = None


class GEOMarketplaceItem(CommonFieldsMixin, Record):
    """Record Metadata manipulation class API."""

    model_cls = GEOMarketplaceItemMetadata

    index = IndexField(
        "marketplaceitems-records-record-v1.0.0",
        search_alias="marketplaceitems-records",
    )

    files = FilesField(
        store=False,
        file_cls=GEOMarketplaceItemFile,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(GEOMarketplaceItemDraft)

    status = DraftStatus()


GEOMarketplaceItemFile.record_cls = GEOMarketplaceItem
GEOMarketplaceItemDraftFile.record_cls = GEOMarketplaceItemDraft
