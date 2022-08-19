# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services schema."""

from invenio_rdm_records.services.schemas import RDMParentSchema as BaseParentSchema
from invenio_rdm_records.services.schemas import RDMRecordSchema as BaseRecordSchema
from marshmallow import fields
from marshmallow_utils.fields import NestedAttribute

from .metadata import MetadataSchema
from .parent import ParentRelationshipSchema


class GEOParentSchema(BaseParentSchema):
    """GEO Knowledge Hub Parent schema."""

    relationship = fields.Nested(ParentRelationshipSchema, dump_only=True)


class GEORecordSchema(BaseRecordSchema):
    """GEO Knowledge Hub Record Schema."""

    metadata = NestedAttribute(MetadataSchema)

    parent = NestedAttribute(GEOParentSchema)
