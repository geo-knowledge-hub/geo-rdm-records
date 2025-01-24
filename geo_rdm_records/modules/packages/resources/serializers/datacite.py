# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Datacite serializers."""

from datacite import schema43
from flask_resources.serializers import MarshmallowJSONSerializer
from invenio_rdm_records.resources.serializers.datacite.schema import (
    DataCite43Schema as BaseDataCite43Schema,
)
from invenio_rdm_records.resources.serializers.utils import get_vocabulary_props
from pydash import py_


#
# Schema
#
class DataCite43Schema(BaseDataCite43Schema):
    """DataCite JSON 4.3 Marshmallow Schema."""

    def get_type(self, obj):
        """Get resource type."""
        # try to get resource type. If not available, use ``knowledge`` as default.
        # this scenario is expected in Knowledge Package cases.
        resource_type_id = py_.get(obj, "metadata.resource_type.id", "knowledge")

        props = get_vocabulary_props(
            "resourcetypes",
            ["props.datacite_general", "props.datacite_type"],
            resource_type_id,
        )

        return {
            "resourceTypeGeneral": props.get("datacite_general", "Other"),
            "resourceType": props.get("datacite_type", ""),
        }


#
# Serializer
#
class DataCite43JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based DataCite serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=DataCite43Schema, **options)


class DataCite43XMLSerializer(DataCite43JSONSerializer):
    """JSON based DataCite XML serializer for records."""

    def serialize_object(self, record, **kwargs):
        """Serialize a single record."""
        data = self.dump_one(record, **kwargs)
        return schema43.tostring(data)

    def serialize_object_list(self, records, **kwargs):
        """Serialize a list of records."""
        return "\n".join(
            [self.serialize_object(rec, **kwargs) for rec in records["hits"]["hits"]]
        )
