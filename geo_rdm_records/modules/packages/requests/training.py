# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Package requests definition."""

from flask_babelex import lazy_gettext as _
from invenio_requests.customizations import RequestType, actions

from geo_rdm_records.proxies import current_requests_notification_service


#
# Actions
#
class SubmitAction(actions.SubmitAction):
    """Submit action."""

    def execute(self, identity, uow):
        """Execute submit action."""
        record = self.request.topic.resolve()
        # Create a custom title for the request
        record_title = record["metadata"]["title"]
        request_title = f"Training request: {record_title}"
        # Defining the custom title for the request
        self.request["title"] = request_title
        super().execute(identity, uow)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept feed post creation."""
        # Use the Assistance requests service to manage the training session.
        current_requests_notification_service.notify_creation(
            identity, self.request, uow=uow
        )

        # Finish operation.
        super().execute(identity, uow)


#
# Request
#
class TrainingSessionRequest(RequestType):
    """Training session request for a Knowledge Package."""

    type_id = "requests-assistance-training-creation"
    name = _("Training session request")

    creator_can_be_none = False
    topic_can_be_none = False

    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["package_record"]

    available_actions = {
        "create": actions.CreateAction,
        "submit": SubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "cancel": actions.CancelAction,
        "decline": actions.DeclineAction,
        "expire": actions.ExpireAction,
    }
