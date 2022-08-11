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
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import FilesField, IndexField

from geo_rdm_records.base.records.systemfields.common import BaseGEORecordsFieldsMixin

from .systemfields.relationship import RecordRelationshipField


#
# Parent record API
#
class GEOParent(BaseRecordParent):
    """Record parent."""

    #
    # System fields
    #
    schema = ConstantField("$schema", "local://records/geo-parent-v1.0.0.json")

    relationship = RecordRelationshipField(key="relationship")


class CommonFieldsMixin(BaseCommonFieldsMixin, BaseGEORecordsFieldsMixin):
    """Common system fields between records and drafts."""

    parent_record_cls = GEOParent
    schema = ConstantField("$schema", "local://records/geo-record-v5.0.0.json")


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
        "geordmrecords-drafts-draft-v5.0.0", search_alias="geordmrecords"
    )

    files = FilesField(
        store=False,
        file_cls=GEOFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()


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
        "geordmrecords-records-record-v5.0.0", search_alias="geordmrecords-records"
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


GEOFileDraft.record_cls = GEODraft
GEOFileRecord.record_cls = GEORecord
