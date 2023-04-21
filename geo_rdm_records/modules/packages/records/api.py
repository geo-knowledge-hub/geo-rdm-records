# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API."""

import enum

from invenio_records.systemfields import ConstantField
from invenio_requests.records.api import Request

from geo_rdm_records.base.records.types import GEORecordTypes
from geo_rdm_records.customizations.records.api import GEODraft as GEODraftBase
from geo_rdm_records.customizations.records.api import GEOParent as GEOParentBase
from geo_rdm_records.customizations.records.api import GEORecord as GEORecordBase

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
class GEOPackageParent(GEOParentBase):
    """Parent record."""

    access = ParentRecordAccessField()

    # Base type
    type = ConstantField("type", GEORecordTypes.package)


#
# Record and Draft APIs.
#
class CommonFieldsMixin:
    """Common system fields between published and draft packages."""

    parent_record_cls = GEOPackageParent


class GEOPackageDraft(CommonFieldsMixin, GEODraftBase):
    """Record (Draft) Metadata manipulation class API."""

    relationship = PackageRelationshipField(key="relationship")

    assistance_requests = AssistanceRequests(
        Request, keys=["type", "receiver", "status"]
    )


class GEOPackageRecord(CommonFieldsMixin, GEORecordBase):
    """Record Metadata manipulation class API."""

    relationship = PackageRelationshipField(key="relationship")

    assistance_requests = AssistanceRequests(
        Request, keys=["type", "receiver", "status"]
    )
