# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Schemas."""

from invenio_rdm_records.services.schemas import RDMRecordSchema as BaseRecordSchema
from invenio_rdm_records.services.schemas.metadata import VocabularySchema
from marshmallow import fields
from marshmallow_utils.fields import NestedAttribute

from geo_rdm_records.base.services.schemas import MetadataSchema as BaseMetadataSchema
from geo_rdm_records.base.services.schemas import ParentSchema
from geo_rdm_records.base.services.schemas.validator import ResourceType

from .relationship import RelationshipSchema


class MetadataSchema(BaseMetadataSchema):
    """Package metadata schema."""

    # Packages are created using the same metadata model as a record, but
    # we can't allow users to define the same values. One example
    # of this is the `resource type`. A package can only have a one
    # resource type, which is the `knowledge` (Knowledge Package type
    # identifier in the GEO Knowledge Hub types vocabulary).
    resource_type = fields.Nested(
        VocabularySchema,
        required=False,
        validate=ResourceType("knowledge"),
        dump_only=False,
    )


class GEOPackageRecordSchema(BaseRecordSchema):
    """Record schema."""

    relationship = fields.Nested(RelationshipSchema, dump_only=True)

    parent = NestedAttribute(ParentSchema)

    metadata = NestedAttribute(MetadataSchema)
