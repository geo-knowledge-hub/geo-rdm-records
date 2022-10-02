# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search resources."""

from flask_resources import route
from invenio_rdm_records.resources.resources import (
    RDMRecordResource as BaseRecordResource,
)


class SearchRecordResource(BaseRecordResource):
    """Record resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            # limiting only search operations.
            route("GET", f"{self.config.url_prefix}{routes['list']}", self.search),
            route(
                "GET",
                f"{routes['user-prefix']}{self.config.url_prefix}",
                self.search_user_records,
            ),
            route("GET", routes["community-records"], self.search_community_records),
        ]
