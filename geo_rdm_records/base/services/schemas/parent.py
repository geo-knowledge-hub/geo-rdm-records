# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services schemas."""

from invenio_rdm_records.services.schemas.parent import (
    RDMParentSchema as BaseParentSchema,
)
from marshmallow import fields
from marshmallow_utils.fields import NestedAttribute

from .harvester import HarvesterSchema


class ParentSchema(BaseParentSchema):
    """Parent schema for the GEO RDM Records."""

    type = fields.String(dump_only=True)

    category = fields.String(dump_only=True)

    harvester = NestedAttribute(HarvesterSchema, required=False)
