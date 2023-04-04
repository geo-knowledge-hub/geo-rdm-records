# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Requests service."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search.engine import dsl
from marshmallow import ValidationError

from geo_rdm_records.base.services.requests import BaseRequestService
from geo_rdm_records.modules.packages.errors import PackageRequestException


class PackageBlogRequestService(BaseRequestService):
    """Blog requests class for Packages."""

    #
    # Request type
    #
    request_type = "blog-post-creation"

    #
    # Topic type
    #
    request_topic_type = "package_record"

    #
    # Auxiliary function
    #
    def _search_record_requests(self, identity, record_pid, extra_filter=None):
        """Search for record requests."""
        # Search rule: Extra filter to search by the specific request type
        # ToDo: Should this filter be available in the `search_record_requests` ?
        extra_filter = dsl.query.Bool(
            "must", must=[dsl.Q("term", **{"type": self.request_type})]
        )

        return super()._search_record_requests(
            identity, record_pid, extra_filter=extra_filter
        )

    #
    # High-Level API
    #
    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Create or update an existing request."""
        # To create a blog post, user must be able to manage the record
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "manage", record=record)

        # Search package requests
        package_requests = self._search_record_requests(identity, id_)

        # If an request exists, delete it
        if package_requests:
            # Assumes that only one request is available
            package_request = package_requests[0]

            # Delete request (following the approach defined in the Invenio RDM Records)
            current_requests_service.delete(identity, package_request["id"], uow=uow)

        return self.create(identity, data, record, uow=uow)

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Submit a request for a Knowledge Package action."""
        if not record.is_published or not (record.versions.index >= 1):
            raise PackageRequestException(
                _("You can only create a blog post for published packages.")
            )

        # Validate the request type
        type_ = data.pop("type", None)
        type_ = current_request_type_registry.lookup(type_, quiet=True)

        if type_ is None:
            raise ValidationError(_("Invalid request type."), field_name="type")

        # Receiver
        receiver = data.pop("receiver", None)
        receiver = ResolverRegistry.resolve_entity_proxy(receiver).resolve()

        # Delegate to requests service to create the request
        return current_requests_service.create(
            identity, data, type_, receiver, topic=record, uow=uow
        )

    @unit_of_work()
    def submit(self, identity, id_, data=None, revision_id=None, uow=None):
        """Submit blog post request."""
        # To create a blog post, user must be able to manage the record
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "manage", record=record)

        # Search package requests
        package_requests = self._search_record_requests(identity, id_)

        # Assumes that only one request is available
        package_request = package_requests[0]

        # Submit!
        request_id = package_request["id"]

        request_item = current_requests_service.execute_action(
            identity, request_id, "submit", data=data, uow=uow
        )

        return request_item
