# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API."""

from invenio_drafts_resources.records import Draft, Record

from invenio_rdm_records.records.systemfields import HasDraftCheckField
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
)

from invenio_rdm_records.records.api import RDMParent as BaseRecordParent

from geo_rdm_records.records.api import CommonFieldsMixin as BaseCommonFieldsMixin
from geo_rdm_records.records.api import GEODraft, GEORecord

import models as geo_models

from .systemfields.access import PackageAccessField
from .systemfields.relatedrecords import RelatedRecordsField


#
# Parent
#
class GEOPackageParent(BaseRecordParent):
    """Parent record."""

    # Configuration
    model_cls = geo_models.GEOPackageParentMetadata


#
# Record and Draft APIs.
#
class CommonFieldsMixin(BaseCommonFieldsMixin):
    """Common system fields between published and draft packages."""

    versions_model_cls = geo_models.GEOPackageVersionsState
    parent_record_cls = GEOPackageParent

    access = PackageAccessField()
    schema = ConstantField("$schema", "local://packages/geo-package-v1.0.0.json")


#
# Draft API.
#
class GEOPackageFileDraft(FileRecord):
    """Record (Draft) File abstraction class."""

    model_cls = geo_models.GEOPackageFileDraftMetadata
    records_cls = None


class GEOPackageDraft(CommonFieldsMixin, Draft):
    """Record (Draft) Metadata manipulation class API."""

    model_cls = geo_models.GEOPackageDraftMetadata

    index = IndexField(
        "geordmpackages-drafts-draft-v1.0.0", search_alias="geordmpackages"
    )

    files = FilesField(
        store=False,
        file_cls=GEOPackageFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()

    # draft packages can be only related with Draft Records.
    resources = RelatedRecordsField(GEODraft)


#
# Record API
#
class GEOPackageFileRecord(FileRecord):
    """Record File abstraction class."""

    model_cls = geo_models.GEOPackageFileRecordMetadata
    records_cls = None


class GEOPackageRecord(CommonFieldsMixin, Record):
    """Record Metadata manipulation class API."""

    model_cls = geo_models.GEOPackageRecordMetadata

    index = IndexField(
        "geordmpackages-records-record-v1.0.0", search_alias="geordmpackages-records"
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

    # draft packages can be only related with Records.
    resources = RelatedRecordsField(GEORecord, key="relationship.resources")


GEOPackageFileDraft.record_cls = GEOPackageDraft
GEOPackageFileRecord.record_cls = GEOPackageRecord
