# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for parameter parsing."""

from invenio_drafts_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow import fields, post_load


class GEOSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Extend schema with `CSL` and `Bounding box` fields."""

    style = fields.Str()
    locale = fields.Str()

    filters = ["bbox"]
    """Filters."""

    @post_load(pass_original=True)
    def facets(self, data, original_data=None, **kwargs):
        """Collect all unknown values into a facets (and filters) key.

        ToDo:
            Review the approach used to define the `filters` items.
        """
        data["facets"] = {}
        data["filters"] = {}
        for k in set(original_data.keys()) - set(data.keys()):

            if k in self.filters:
                data["filters"][k] = original_data.get(k)
            else:
                data["facets"][k] = original_data.getlist(k)
        return data
