# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Items Models."""


from invenio_communities.records.records.models import CommunityRelationMixin
from invenio_db import db
from invenio_drafts_resources.records import (
    DraftMetadataBase,
    ParentRecordMixin,
    ParentRecordStateMixin,
)
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records import FileRecordModelMixin
from sqlalchemy_utils.types import UUIDType


#
# Parent
#
class GEOMarketplaceItemParentMetadata(db.Model, RecordMetadataBase):
    """Parent metadata."""

    __tablename__ = "geo_marketplace_parents_metadata"


class GEOMarketplaceItemParentCommunityMetadata(db.Model, CommunityRelationMixin):
    """Parent relation with communities."""

    __tablename__ = "geo_marketplace_parents_community"
    __record_model__ = GEOMarketplaceItemParentMetadata


#
# Records
#
class GEOMarketplaceItemMetadata(db.Model, RecordMetadataBase, ParentRecordMixin):
    """Marketplace item."""

    __tablename__ = "geo_marketplace_items_metadata"
    __parent_record_model__ = GEOMarketplaceItemParentMetadata

    # Enable versioning
    __versioned__ = {}

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class GEOMarketplaceItemFileMetadata(
    db.Model, RecordMetadataBase, FileRecordModelMixin
):
    """File associated with an item."""

    __record_model_cls__ = GEOMarketplaceItemMetadata

    __tablename__ = "geo_marketplace_items_files"


#
# Drafts
#
class GEOMarketplaceItemDraftMetadata(db.Model, DraftMetadataBase, ParentRecordMixin):
    """Marketplace Item Draft."""

    __tablename__ = "geo_marketplace_drafts_metadata"
    __parent_record_model__ = GEOMarketplaceItemParentMetadata

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class GEOMarketplaceItemDraftFileMetadata(
    db.Model, RecordMetadataBase, FileRecordModelMixin
):
    """File associated with a draft item."""

    __record_model_cls__ = GEOMarketplaceItemDraftMetadata

    __tablename__ = "geo_marketplace_drafts_files"


#
# Versions state
#
class GEOMarketplaceItemVersionsState(db.Model, ParentRecordStateMixin):
    """Marketplace item version state."""

    __tablename__ = "geo_marketplace_versions_state"

    __parent_record_model__ = GEOMarketplaceItemParentMetadata
    __record_model__ = GEOMarketplaceItemMetadata
    __draft_model__ = GEOMarketplaceItemDraftMetadata
