# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API."""

import enum

import invenio_rdm_records.records.models as rdm_models
from invenio_drafts_resources.records import Draft, Record
from invenio_rdm_records.records.api import CommonFieldsMixin as BaseCommonFieldsMixin
from invenio_rdm_records.records.api import RDMParent as BaseRecordParent
from invenio_rdm_records.records.systemfields import HasDraftCheckField
from invenio_rdm_records.records.systemfields.draft_status import DraftStatus
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import FilesField, IndexField
from invenio_requests.records.api import Request

from geo_rdm_records.base.records.api import GEOBaseRecord
from geo_rdm_records.base.records.systemfields.common import BaseGEORecordsFieldsMixin
from geo_rdm_records.base.records.types import GEORecordTypes

from .systemfields.access import ParentRecordAccessField
from .systemfields.relationship import PackageRelationshipField
from .systemfields.requests import AssistanceRequests


#
# Enum
#
class PackageRelationship(enum.Enum):
    """Package relationship types."""

    RELATED = "related"
    """Related relationship."""

    MANAGED = "managed"
    """Managed relationship."""


#
# Parent
#
class GEOPackageParent(GEOBaseRecord, BaseRecordParent):
    """Parent record."""

    # Configuration
    access = ParentRecordAccessField()
    schema = ConstantField("$schema", "local://records/geo-parent-v1.0.0.json")

    type = ConstantField("type", GEORecordTypes.package)


#
# Record and Draft APIs.
#
class CommonFieldsMixin(BaseGEORecordsFieldsMixin, BaseCommonFieldsMixin):
    """Common system fields between published and draft packages."""

    # versions_model_cls = GEOPackageVersionsState
    parent_record_cls = GEOPackageParent

    schema = ConstantField("$schema", "local://records/geo-record-v1.0.0.json")


#
# Draft API.
#
class GEOPackageFileDraft(FileRecord):
    """Record (Draft) File abstraction class."""

    model_cls = rdm_models.RDMFileDraftMetadata
    records_cls = None


class GEOPackageDraft(CommonFieldsMixin, Draft):
    """Record (Draft) Metadata manipulation class API."""

    model_cls = rdm_models.RDMDraftMetadata

    index = IndexField(
        "geordmrecords-drafts-draft-v1.0.0", search_alias="geordmrecords"
    )

    files = FilesField(
        store=False,
        file_cls=GEOPackageFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()

    status = DraftStatus()

    relationship = PackageRelationshipField(key="relationship")

    assistance_requests = AssistanceRequests(
        Request, keys=["type", "receiver", "status"]
    )


#
# Record API
#
class GEOPackageFileRecord(FileRecord):
    """Record File abstraction class."""

    model_cls = rdm_models.RDMFileRecordMetadata
    records_cls = None


class GEOPackageRecord(CommonFieldsMixin, Record):
    """Record Metadata manipulation class API."""

    model_cls = rdm_models.RDMRecordMetadata

    index = IndexField(
        "geordmrecords-records-record-v1.0.0", search_alias="geordmrecords-records"
    )

    files = FilesField(
        store=False,
        file_cls=GEOPackageFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(GEOPackageDraft)

    status = DraftStatus()

    relationship = PackageRelationshipField(key="relationship")

    assistance_requests = AssistanceRequests(
        Request, keys=["type", "receiver", "status"]
    )


GEOPackageFileDraft.record_cls = GEOPackageDraft
GEOPackageFileRecord.record_cls = GEOPackageRecord
