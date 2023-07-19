# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Records API."""

import invenio_rdm_records.records.api as rdm_api
from invenio_rdm_records.records.systemfields import HasDraftCheckField
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.systemfields import IndexField

from geo_rdm_records.base.records.api import GEOBaseRecord
from geo_rdm_records.base.records.systemfields.common import BaseGEORecordsFieldsMixin
from geo_rdm_records.base.records.types import GEORecordTypes

from .systemfields.relationship import (
    PackageRelationshipField,
    RecordParentRelationshipField,
)


#
# Parent record API
#
class GEOParent(GEOBaseRecord, rdm_api.RDMParent):
    """Record parent."""

    #
    # System fields
    #
    type = ConstantField("type", GEORecordTypes.resource)

    # ToDo: Move the `jsonschemas` to the `base` module
    schema = ConstantField("$schema", "local://records/geo-parent-v1.0.0.json")

    relationship = RecordParentRelationshipField(key="relationship")


class CommonFieldsMixin(BaseGEORecordsFieldsMixin, rdm_api.CommonFieldsMixin):
    """Common system fields between records and drafts."""

    parent_record_cls = GEOParent
    schema = ConstantField("$schema", "local://records/geo-record-v1.0.0.json")


#
# Draft API
#
class GEODraft(CommonFieldsMixin, rdm_api.RDMDraft):
    """Record (Draft) Metadata manipulation class API."""

    index = IndexField(
        "geordmrecords-drafts-draft-v1.0.0", search_alias="geordmrecords"
    )

    relationship = PackageRelationshipField(key="relationship")


#
# Record API
#
class GEORecord(CommonFieldsMixin, rdm_api.RDMRecord):
    """Record Metadata manipulation class API."""

    index = IndexField(
        "geordmrecords-records-record-v1.0.0", search_alias="geordmrecords-records"
    )

    has_draft = HasDraftCheckField(GEODraft)
    relationship = PackageRelationshipField(key="relationship")
