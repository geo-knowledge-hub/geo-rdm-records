# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resource Rest resource."""

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_rdm_records.resources import RDMRecordResource as BaseRecordResource
from invenio_records_resources.resources.records.resource import (
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference


class GEORDMRecordResource(BaseRecordResource):
    """RDM record resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        url_rules = super().create_url_rules()
        url_rules += [
            # Packages API (with prefix included).
            route("GET", routes["item-resources-search"], self.search_package_records),
            route(
                "GET", routes["item-draft-resources-search"], self.search_package_drafts
            ),
            route(
                "GET",
                routes["item-context-resources-search"],
                self.search_package_context_versions,
            ),
        ]

        return url_rules

    #
    # Package records
    #
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search_package_records(self):
        """Perform a search over the package resources."""
        hits = self.service.search_package_records(
            identity=g.identity,
            package_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
        )
        return hits.to_dict(), 200

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search_package_drafts(self):
        """Perform a search over the package (draft) resources."""
        hits = self.service.search_package_drafts(
            identity=g.identity,
            package_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
        )
        return hits.to_dict(), 200

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search_package_context_versions(self):
        """Perform a search over the records and drafts of a package."""
        hits = self.service.search_package_context_versions(
            identity=g.identity,
            package_parent_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
        )
        return hits.to_dict(), 200
