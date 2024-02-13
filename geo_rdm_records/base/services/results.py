# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services results."""

from invenio_records_resources.services.records.results import (
    RecordList as BaseRecordList,
)

from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)
from geo_rdm_records.modules.rdm.records.api import GEODraft, GEORecord


class ResultRegistryType:
    """Result types for mutable search results."""

    supported_types = {
        "packages": dict(
            draft=GEOPackageDraft,
            record=GEOPackageRecord,
        ),
        "records": dict(draft=GEODraft, record=GEORecord),
    }

    @classmethod
    def guess_type(cls, obj, error=True):
        """Guess object type based on the types available."""
        for key in cls.supported_types.keys():
            cls_type = "draft"

            schema_ = obj.get("$schema", "")
            schema_parent_ = obj.get("parent", {}).get("$schema", "")

            if key in schema_ or key in schema_parent_:
                if obj.get("is_published", False):
                    cls_type = "record"

                # creating the object
                return cls.supported_types[key][cls_type].loads(obj)

        if error:
            raise RuntimeError("Not able to mutate the record: Type not supported")


class MutableRecordList(BaseRecordList):
    """List of records result."""

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results:
            # Load dump
            record = self._service.results_registry_type.guess_type(hit.to_dict())

            # Project the record
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                ),
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )

            yield projection
