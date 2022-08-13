# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Schemas."""

from marshmallow import Schema, fields, validate


class ResourceEntitySchema(Schema):
    """Represents a single resource entity."""

    type = fields.String(required=True, validate=validate.OneOf(["managed", "related"]))
    id = fields.String(required=True)


class ResourcesSchema(Schema):
    """Resources schema."""

    resources = fields.List(
        fields.Nested(ResourceEntitySchema),
        # (Tip from Invenio Communities) max is on purpose to limit
        # the max number of additions/changes/removals per request
        # as they all run in a single transaction and requires resources
        # to hold.
        validate=validate.Length(min=1, max=100),
    )
