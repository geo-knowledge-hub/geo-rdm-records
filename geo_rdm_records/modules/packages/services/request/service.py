# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Requests service."""

from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from marshmallow import ValidationError

from geo_rdm_records.modules.packages.errors import (
    PackageRequestException,
    PackageRequestNotFoundError,
)


#
# Utility
#
def has_feed_requests(record, ctx):
    """Shortcut for links to determine if record has ."""
    return any(
        map(
            lambda x: x["type"] == PackageFeedRequestService.request_type,
            record.assistance_requests,
        )
    )


class PackageFeedRequestService(RecordService):
    """Feed requests class for Packages."""

    #
    # Request type
    #
    request_type = "feed-post-creation"

    #
    # Topic type
    #
    request_topic_type = "package_record"

    #
    # Properties
    #
    @property
    def _default_receiver(self):
        return self.config.request_default_receiver

    #
    # Auxiliary function
    #
    def _search_record_requests(self, record):
        """Search for record requests."""
        # Search rule: Extra filter to search by the specific request type
        package_requests = record.assistance_requests

        for request in package_requests:
            # checking the type of the request
            request = request.get_object()

            if self.request_type == request.type.type_id:
                # Assumes that only one request is available
                return request
        return None

    #
    # High-Level API
    #
    def read(self, identity, id_):
        """Read request."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "manage", record=record)

        # Get package requests
        request = self._search_record_requests(record)

        if request:
            # reusing request service to avoid read the same
            # record many times.
            return current_requests_service.result_item(
                current_requests_service,
                identity,
                request,
                schema=current_requests_service._wrap_schema(
                    request.type.marshmallow_schema()
                ),
                links_tpl=current_requests_service.links_item_tpl,
                expandable_fields=current_requests_service.expandable_fields,
                expand=False,
            )

        raise PackageRequestNotFoundError()

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Create or update an existing request."""
        # To create a feed post, user must be able to manage the record
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "manage", record=record)

        # Get package requests
        request = self._search_record_requests(record)

        if request:
            current_requests_service.delete(identity, request.id, uow=uow)
        return self.create(identity, data, record, uow=uow)

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Submit a request for a Knowledge Package action."""
        if not record.is_published or not (record.versions.index >= 1):
            raise PackageRequestException(
                _("You can only create a feed post for published packages.")
            )

        # Validate the request type
        type_ = data.pop("type", None)
        type_ = current_request_type_registry.lookup(type_, quiet=True)

        if type_ is None:
            raise ValidationError(_("Invalid request type."), field_name="type")

        # Receiver
        # ToDo: Can we add groups as default ?
        receiver = {"user": self._default_receiver}
        receiver = ResolverRegistry.resolve_entity_proxy(receiver).resolve()

        # Delegate to requests service to create the request
        request_item = current_requests_service.create(
            identity, data, type_, receiver, topic=record, uow=uow
        )

        # Save request in the record
        record.assistance_requests.append(request_item._request)
        uow.register(RecordCommitOp(record))

        return request_item

    @unit_of_work()
    def submit(self, identity, id_, data=None, revision_id=None, uow=None):
        """Submit feed post request."""
        # To create a feed post, user must be able to manage the record
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "manage", record=record)

        # Search package requests
        request = self._search_record_requests(record)

        if request:
            return current_requests_service.execute_action(
                identity, request.id, "submit", data=data, uow=uow
            )
