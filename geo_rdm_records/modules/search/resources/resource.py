# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search resources."""

from flask_resources import route
from invenio_records_resources.resources.records.resource import (
    RecordResource as BaseRecordResource,
)


class SearchRecordResource(BaseRecordResource):
    """Record resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            # limiting only search operations.
            route("GET", routes["list"], self.search),
            # route("POST", routes["list"], self.search),
        ]
