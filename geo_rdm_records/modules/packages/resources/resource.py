# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource for the Packages API."""

from flask import g
from flask_resources import resource_requestctx, route
from invenio_drafts_resources.resources import RecordResource
from invenio_rdm_records.resources.resources import (
    RDMParentRecordLinksResource as BaseParentRecordLinksResource,
)
from invenio_rdm_records.resources.resources import (
    RDMRecordResource as BaseRecordResource,
)
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_view_args,
)


class GEOPackageParentRecordLinksResource(BaseParentRecordLinksResource):
    """Secret links resource."""


class GEOPackageRecordResource(BaseRecordResource):
    """Record resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        url_rules = super().create_url_rules()
        url_rules += [
            # Packages Resources (Draft operations)
            route("POST", p(routes["item-draft-resources"]), self.package_add_resource),
            route(
                "DELETE",
                p(routes["item-draft-resources"]),
                self.package_delete_resource,
            ),
            route(
                "POST",
                p(routes["item-resources-import"]),
                self.package_import_resources,
            ),
            route("POST", p(routes["item-validate"]), self.package_validate)
            # route("PUT", p(routes["item-draft-resources"]), self.resource_update_draft)
        ]

        return url_rules

    #
    # Resources (Draft)
    #
    @request_view_args
    def package_import_resources(self):
        """Import resources from previous package version."""
        self.service.import_resources(
            g.identity, resource_requestctx.view_args["pid_value"]
        )

        return "", 204

    @request_view_args
    @request_data
    def package_add_resource(self):
        """Add resources to a package."""
        result = self.service.resource_add(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        # ``result`` can contain a list of errors.
        # in this case, we return ``200``, because the
        # operation is done, even though some parts have errors
        return result, 200

    @request_view_args
    @request_data
    def package_delete_resource(self):
        """Add resources to a package."""
        result = self.service.resource_delete(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        # ``result`` can contain a list of errors.
        # in this case, we return ``200``, because the
        # operation is done, even though some parts have errors
        return result, 200

    @request_view_args
    def package_validate(self):
        """Check if a package is valid."""
        result = self.service.validate_package(
            g.identity,
            resource_requestctx.view_args["pid_value"],
        )
        return result, 200


class GEOPackageContextResource(RecordResource):
    """Package context resource."""

    def create_url_rules(self):
        """Create the URL rules for the context resource."""

        def p(route):
            """Prefix a  route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        return [
            # route(
            #     "GET", p(routes["list"]), self.context
            # ),
            route("PUT", p(routes["context"]), self.context_update),
            route("POST", p(routes["context-associate"]), self.context_associate),
            route("POST", p(routes["context-dissociate"]), self.context_dissociate),
        ]

    #
    # Resources
    #
    @request_view_args
    @request_data
    def context_update(self):
        """Associate record in a package context."""
        self.service.context_update(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return "", 204

    @request_view_args
    @request_data
    def context_associate(self):
        """Associate record in a package context."""
        self.service.context_associate(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return "", 204

    @request_view_args
    @request_data
    def context_dissociate(self):
        """Associate record in a package context."""
        self.service.context_dissociate(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            resource_requestctx.data,
        )
        return "", 204
