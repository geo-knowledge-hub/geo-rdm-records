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
def has_assistance_requests(record, ctx):
    """Shortcut for links to determine if record has ."""
    return any(
        map(
            lambda x: x["type"] in PackageRequestsService.request_type,
            record.assistance_requests,
        )
    )


class PackageRequestsService(RecordService):
    """Feed requests class for Packages."""

    #
    # Request type
    #
    request_type = [
        "requests-assistance-feed-creation",
        "requests-assistance-training-creation",
    ]

    #
    # Request permissions
    #
    request_permissions = {
        "requests-assistance-feed-creation": "manage",
        "requests-assistance-training-creation": "create",
    }

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
    def _search_record_requests(self, record, identity, exclude=None):
        """Search for record requests."""
        exclude = exclude or []

        # Search rule: Extra filter to search by the specific request type
        package_requests = record.assistance_requests

        for request in package_requests:
            # checking the type of the request
            request = request.get_object()

            if request.type.type_id in self.request_type:
                # ToDo: Assumes that only one request is available per user.
                #       Remove this on version 1.7.0 with the InvenioRDM requests endpoint.
                is_request_creator = request.created_by.resolve().id == identity.id
                is_cancelled = request.status == "cancelled"
                is_valid = request.status not in exclude

                if is_request_creator and not is_cancelled and is_valid:
                    return request
        return None

    def _define_permission(self, request_type):
        """Define the permission required based on ``Request Type``."""
        return self.request_permissions.get(request_type)

    #
    # High-Level API
    #
    def read(self, identity, id_):
        """Read request."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        request = self._search_record_requests(record, identity)

        self.require_permission(identity, "read", request=request)

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
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        request = self._search_record_requests(record, identity, exclude=["submitted"])

        if request:
            return current_requests_service.update(
                identity, request.id, data=data, revision_id=revision_id, uow=uow
            )
        return self.create(identity, data, record, uow=uow)

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Submit a request for a Knowledge Package action."""
        # Validate the request type
        type_name = data.pop("type", None)
        type_object = current_request_type_registry.lookup(type_name, quiet=True)

        if type_object is None:
            raise ValidationError(_("Invalid request type."), field_name="type")

        # Validate permission
        permission = self._define_permission(type_name)
        self.require_permission(identity, permission, record=record)

        # Validate package status
        if not record.is_published or not (record.versions.index >= 1):
            raise PackageRequestException(
                _("You can only create a feed post for published packages.")
            )

        # Receiver
        # ToDo: Can we add groups as default ?
        receiver = {"user": self._default_receiver}
        receiver = ResolverRegistry.resolve_entity_proxy(receiver).resolve()

        # Delegate to requests service to create the request
        request_item = current_requests_service.create(
            identity, data, type_object, receiver, topic=record, uow=uow
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
        request = self._search_record_requests(record, identity, exclude=["submitted"])

        self.require_permission(identity, "action_submit", request=request)

        if request:
            return current_requests_service.execute_action(
                identity, request.id, "submit", data=data, uow=uow
            )
