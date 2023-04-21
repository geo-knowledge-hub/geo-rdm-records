# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Community submission."""

from flask_babelex import lazy_gettext as _
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_records_resources.services.uow import RecordCommitOp, RecordIndexOp
from invenio_requests.customizations import actions

from geo_rdm_records.customizations import GEODraft, GEORecord
from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)
from geo_rdm_records.proxies import current_geo_packages_service


class ServiceHandler:
    """Service handler class for actions.

    This class add the support for multiple ``services`` based on
    different classes. This implementation was created to support
    the use of the same set of actions with multiple services and
    entities.

    ToDo:
        This is the best approach ? Do Invenio Requests provide
        another way to handle this ?
    """

    services = [
        {
            "type": "resource",
            "service": current_rdm_records_service,
        },
        {
            "type": "package",
            "service": current_geo_packages_service,
        },
    ]
    """Definition of the services available to handle actions."""

    def _get_service(self, record):
        """Select the service.

        Select the service based on the ``record`` type.
        """
        for service in self.services:
            if record.parent.type == service["type"]:
                return service["service"]

        raise ValueError(_(f"Invalid record type: {record.parent.type}"))


#
# Actions
#
class SubmitAction(actions.SubmitAction, ServiceHandler):
    """Submit action.

    Note:
        We adapted this class from ``Invenio RDM Records`` to add the
        support for multiple services.
    """

    def execute(self, identity, uow):
        """Execute the submit action."""
        # defining the service
        draft = self.request.topic.resolve()
        service = self._get_service(draft)

        service._validate_draft(identity, draft)

        # Set the record's title as the request title.
        self.request["title"] = draft.metadata["title"]
        super().execute(identity, uow)


class AcceptAction(actions.AcceptAction, ServiceHandler):
    """Accept action.

    Note:
        We adapted this class from ``Invenio RDM Records`` to add the
        support for multiple services.
    """

    def execute(self, identity, uow):
        """Accept record into community."""
        # Resolve the topic and community - the request type only allow for
        # community receivers and record topics.
        draft = self.request.topic.resolve()
        service = self._get_service(draft)

        community = self.request.receiver.resolve()
        service._validate_draft(identity, draft)

        # Unset review from record (still accessible from request)
        # The curator (receiver) should still have access, via the community
        # The creator (uploader) should also still have access, because
        # they're the uploader
        draft.parent.review = None

        # TODO:
        # - Put below into a service method
        # - Check permissions

        # Add community to record.
        is_default = self.request.type.set_as_default
        draft.parent.communities.add(
            community, request=self.request, default=is_default
        )
        uow.register(RecordCommitOp(draft.parent))

        # Publish the record
        # TODO: Ensure that the accpeting user has permissions to publish.
        service.publish(identity, draft.pid.pid_value, uow=uow)
        super().execute(identity, uow)


class DeclineAction(actions.DeclineAction, ServiceHandler):
    """Decline action.

    Note:
        We adapted this class from ``Invenio RDM Records`` to add the
        support for multiple services.
    """

    def execute(self, identity, uow):
        """Execute action."""
        # Keeps the record and the review connected so the user can see the
        # outcome of the request
        # The receiver (curator) won't have access anymore to the draft
        # The creator (uploader) should still have access to the record/draft
        draft = self.request.topic.resolve()

        service = self._get_service(draft)

        super().execute(identity, uow)

        # TODO: this shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = self.request
        uow.register(RecordCommitOp(draft.parent))
        # update draft to reflect the new status
        uow.register(RecordIndexOp(draft, indexer=service.indexer))


class CancelAction(actions.CancelAction, ServiceHandler):
    """Decline action.

    Note:
        We adapted this class from ``Invenio RDM Records`` to add the
        support for multiple services.
    """

    def execute(self, identity, uow):
        """Execute action."""
        # Remove draft from request
        # Same reasoning as in 'decline'
        draft = self.request.topic.resolve()
        service = self._get_service(draft)

        draft.parent.review = None
        uow.register(RecordCommitOp(draft.parent))
        # update draft to reflect the new status
        uow.register(RecordIndexOp(draft, indexer=service.indexer))
        super().execute(identity, uow)


class ExpireAction(actions.CancelAction, ServiceHandler):
    """Expire action.

    Note:
        We adapted this class from ``Invenio RDM Records`` to add the
        support for multiple services.
    """

    def execute(self, identity, uow):
        """Execute action."""
        # Same reasoning as in 'decline'
        draft = self.request.topic.resolve()
        service = self._get_service(draft)

        # TODO: What more to do? simply close the request? Similarly to
        # decline, how does a user resubmits the request to the same community.
        super().execute(identity, uow)

        # TODO: this shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = self.request
        uow.register(RecordCommitOp(draft.parent))
        # update draft to reflect the new status
        uow.register(RecordIndexOp(draft, indexer=service.indexer))
