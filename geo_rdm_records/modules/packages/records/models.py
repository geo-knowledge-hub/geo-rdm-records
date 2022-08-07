# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Record Packages Models."""


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
class GEOPackageParentMetadata(db.Model, RecordMetadataBase):
    """Metadata store for the package parent record."""

    __tablename__ = "geo_package_parents_metadata"


class GEOPackageParentCommunity(db.Model, CommunityRelationMixin):

    __tablename__ = "geo_package_parents_community"
    __record_model__ = GEOPackageParentMetadata


#
# Records
#
class GEOPackageRecordMetadata(db.Model, RecordMetadataBase, ParentRecordMixin):
    """Represent a bibliographic record metadata (Package version)."""

    __tablename__ = "geo_package_records_metadata"
    __parent_record_model__ = GEOPackageParentMetadata


class GEOPackageFileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a record (Package version)."""

    __record_model_cls__ = GEOPackageRecordMetadata

    __tablename__ = "geo_package_records_files"


#
# Drafts
#
class GEOPackageDraftMetadata(db.Model, DraftMetadataBase, ParentRecordMixin):

    __tablename__ = "geo_package_drafts_metadata"
    __parent_record_model__ = GEOPackageParentMetadata


class GEOPackageFileDraftMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):

    __record_model_cls__ = GEOPackageDraftMetadata

    __tablename__ = "geo_package_drafts_files"


#
# Versions state
#
class GEOPackageVersionsState(db.Model, ParentRecordStateMixin):

    __tablename__ = "geo_package_versions_state"

    __parent_record_model__ = GEOPackageParentMetadata
    __record_model__ = GEOPackageRecordMetadata
    __draft_model__ = GEOPackageDraftMetadata
