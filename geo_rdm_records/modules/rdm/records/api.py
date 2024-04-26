# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Records API."""

import invenio_rdm_records.records.models as rdm_models
from invenio_drafts_resources.records import Draft, Record
from invenio_rdm_records.records.api import CommonFieldsMixin as BaseCommonFieldsMixin
from invenio_rdm_records.records.api import RDMParent as BaseRecordParent
from invenio_rdm_records.records.systemfields import HasDraftCheckField
from invenio_rdm_records.records.systemfields.draft_status import DraftStatus
from invenio_records.systemfields import ConstantField, DictField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import FilesField, IndexField

from geo_rdm_records.base.records.api import GEOBaseRecord
from geo_rdm_records.base.records.categories import GEORecordCategories
from geo_rdm_records.base.records.systemfields.common import BaseGEORecordsFieldsMixin
from geo_rdm_records.base.records.types import GEORecordTypes

from .systemfields.relationship import (
    PackageRelationshipField,
    RecordParentRelationshipField,
)


#
# Parent record API
#
class GEOParent(GEOBaseRecord, BaseRecordParent):
    """Record parent."""

    #
    # System fields
    #
    type = ConstantField("type", GEORecordTypes.resource)

    category = ConstantField("category", GEORecordCategories.open)

    schema = ConstantField("$schema", "local://records/geo-parent-v1.0.0.json")

    relationship = RecordParentRelationshipField(key="relationship")

    harvester = DictField("harvester")


class CommonFieldsMixin(BaseGEORecordsFieldsMixin, BaseCommonFieldsMixin):
    """Common system fields between records and drafts."""

    parent_record_cls = GEOParent
    schema = ConstantField(
        "$schema", "local://records/geordmrecords-records-record-v1.0.0.json"
    )


#
# Draft API
#
class GEOFileDraft(FileRecord):
    """Record (Draft) File abstraction class."""

    model_cls = rdm_models.RDMFileDraftMetadata
    records_cls = None


class GEODraft(CommonFieldsMixin, Draft):
    """Record (Draft) Metadata manipulation class API."""

    model_cls = rdm_models.RDMDraftMetadata

    index = IndexField(
        "geordmrecords-drafts-draft-v1.0.0", search_alias="geordmrecords"
    )

    files = FilesField(
        store=False,
        file_cls=GEOFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()

    status = DraftStatus()

    relationship = PackageRelationshipField(key="relationship")


#
# Record API
#
class GEOFileRecord(FileRecord):
    """Record File abstraction class."""

    model_cls = rdm_models.RDMFileRecordMetadata
    records_cls = None


class GEORecord(CommonFieldsMixin, Record):
    """Record Metadata manipulation class API."""

    model_cls = rdm_models.RDMRecordMetadata

    index = IndexField(
        "geordmrecords-records-record-v1.0.0", search_alias="geordmrecords-records"
    )

    files = FilesField(
        store=False,
        file_cls=GEOFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(GEODraft)

    status = DraftStatus()
    relationship = PackageRelationshipField(key="relationship")


GEOFileDraft.record_cls = GEODraft
GEOFileRecord.record_cls = GEORecord
