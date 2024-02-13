# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Parent Relationship Schemas."""

from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


class RelationshipResourceSchema(Schema):
    """Schema for the Resource used in the RelationshipSchema."""

    id = SanitizedUnicode(required=True)


class ParentRelationshipSchema(Schema):
    """Schema for the Record relationship."""

    # Managed resource
    managed_by = fields.Nested(RelationshipResourceSchema)
