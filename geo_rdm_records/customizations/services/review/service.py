# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service."""

from flask_babelex import lazy_gettext as _
from invenio_communities.communities.records.systemfields.access import CommunityAccess
from invenio_rdm_records.records.systemfields.access.field.record import (
    AccessStatusEnum,
)
from invenio_rdm_records.services.errors import (
    ReviewExistsError,
    ReviewInconsistentAccessRestrictions,
    ReviewNotFoundError,
    ReviewStateError,
)
from invenio_rdm_records.services.review import ReviewService as BaseReviewService
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from marshmallow import ValidationError

from ...records.api import GEODraft, GEORecord
from .errors import ReviewInconsistentResourceRestrictions


class ReviewService(BaseReviewService):
    """Record review service."""

    #
    # Internal methods
    #
    def _validate_record_association(self, record):
        """Check if a record is associated with a package."""
        if isinstance(record, (GEODraft, GEORecord)):
            if record.parent.relationship.managed_by:
                raise ReviewInconsistentResourceRestrictions()

    #
    # High-level API
    #
    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Create a new review request in draft state.

        Note:
            This method was adapted from ``Invenio RDM Records`` to add a specific
            constraint about Knowledge Resources. By default, a Knowledge Resource
            associated with a Knowledge Package can't be associated with a community
            by itself. So, we validate this in this method.

        ToDo:
            - Probably we need to use a better and more 'clear' way to do this verification;
            - Maybe, this service can use the ``Constrained Component``.
        """
        if record.parent.review is not None:
            raise ReviewExistsError(_("A review already exists for this record"))

        # Validate that record has not been published.
        if record.is_published or record.versions.index > 1:
            raise ReviewStateError(
                _("You cannot create a review for an already published " "record.")
            )

        # Validate the record association
        self._validate_record_association(record)

        # Validate the review type (only review requests are valid)
        type_ = current_request_type_registry.lookup(data.pop("type", None), quiet=True)
        if type_ is None or type_.type_id not in self.supported_types:
            raise ValidationError(_("Invalid review type."), field_name="type")

        # Resolve receiver
        receiver = ResolverRegistry.resolve_entity_proxy(
            data.pop("receiver", None)
        ).resolve()

        # Delegate to requests service to create the request
        request_item = current_requests_service.create(
            identity,
            data,
            type_,
            receiver,
            topic=record,
            uow=uow,
        )

        # Set the request on the record and commit the record
        record.parent.review = request_item._request
        uow.register(RecordCommitOp(record.parent))
        return request_item

    @unit_of_work()
    def submit(self, identity, id_, data=None, revision_id=None, uow=None):
        """Submit record for review.

        Note:
            This method was adapted from ``Invenio RDM Records`` to add a specific
            constraint about Knowledge Resources. By default, a Knowledge Resource
            associated with a Knowledge Package can't be associated with a community
            by itself. So, we validate this in this method.

        ToDo:
            - Probably we need to use a better and more 'clear' way to do this verification;
            - Maybe, this service can use the ``Constrained Component``.
        """
        # Get record and check permission
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "update_draft", record=draft)

        # Preconditions
        if draft.parent.review is None:
            raise ReviewNotFoundError()

        # since it is submit review action, assume the receiver is community
        resolved_community = draft.parent.review.receiver.resolve()

        assert "restricted" in CommunityAccess.VISIBILITY_LEVELS
        community_is_restricted = (
            resolved_community["access"]["visibility"] == "restricted"
        )

        record_is_restricted = draft.access.status == AccessStatusEnum.RESTRICTED

        if community_is_restricted and not record_is_restricted:
            raise ReviewInconsistentAccessRestrictions()

        # Validate the record association
        self._validate_record_association(draft)

        # Notes from Invenio RDM Records:
        #    All other preconditions can be checked by the action itself which can
        #    raise appropriate exceptions.
        request_item = current_requests_service.execute_action(
            identity, draft.parent.review.id, "submit", data=data, uow=uow
        )

        # Notes from Invenio RDM Records:
        #   TODO: this shouldn't be required BUT because of the caching mechanism
        #         in the review systemfield, the review should be set with the updated
        #         request object
        draft.parent.review = request_item._request
        uow.register(RecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))

        return request_item
