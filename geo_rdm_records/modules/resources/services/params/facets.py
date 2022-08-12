# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Facets Params."""

from invenio_records_resources.services.records.params.facets import (
    FacetsParam as BaseFacetsParam,
)


class FacetsParam(BaseFacetsParam):
    """Evaluate facets."""

    def filter(self, search):
        """Apply a post filter on the search.

        Note:
            This method overwrites the original filter to change the facet operator
            from `should` to `must`.
        """
        if not self._filters:
            return search

        filters = list(self._filters.values())

        post_filter = filters[0]
        for f in filters[1:]:
            post_filter &= f

        return search.post_filter(post_filter)
