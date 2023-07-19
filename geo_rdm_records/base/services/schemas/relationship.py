# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Relationship Schemas."""

from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


class RelationshipElementSchema(Schema):
    """Schema for the Element used in the RelationshipSchema."""

    id = SanitizedUnicode(required=True)
    relation_type = fields.Str(required=True)
