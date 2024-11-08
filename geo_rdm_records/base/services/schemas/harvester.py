# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Harvester field."""

from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


class HarvesterSoftwareSchema(Schema):
    """Harvester software schema."""

    name = SanitizedUnicode(required=True)

    version = SanitizedUnicode(required=True)


class HarvesterOriginSchema(Schema):
    """Harvester origin schema."""

    name = SanitizedUnicode(required=True)

    id = SanitizedUnicode(required=True)


class HarvesterSchema(Schema):
    """Harvester schema."""

    software = fields.Nested(HarvesterSoftwareSchema)

    origin = fields.Nested(HarvesterOriginSchema)
