# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services schema."""

from invenio_rdm_records.services.schemas import RDMRecordSchema as BaseRecordSchema
from marshmallow import fields
from marshmallow_utils.fields import NestedAttribute

from geo_rdm_records.base.services.schemas import MetadataSchema, ParentSchema

from .parent import ParentRelationshipSchema
from .relationship import RelationshipSchema


class GEOParentSchema(ParentSchema):
    """GEO Knowledge Hub Parent schema."""

    relationship = fields.Nested(ParentRelationshipSchema, dump_only=True)


class GEORecordSchema(BaseRecordSchema):
    """GEO Knowledge Hub Record Schema."""

    relationship = fields.Nested(RelationshipSchema, dump_only=True)

    parent = NestedAttribute(GEOParentSchema)

    metadata = NestedAttribute(MetadataSchema)
