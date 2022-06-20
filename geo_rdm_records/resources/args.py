# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for parameter parsing."""

from invenio_drafts_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow import fields


class GEOSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Extend schema with CSL and Location fields."""

    style = fields.Str()
    locale = fields.Str()
    location = fields.Str()
