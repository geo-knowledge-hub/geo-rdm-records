# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records feed post requests."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_requests.customizations import RequestType, actions
from sqlalchemy.exc import NoResultFound

from geo_rdm_records.modules.requests.notification.handler import (
    BaseNotificationHandler,
)
from geo_rdm_records.proxies import current_geo_packages_service


#
# Notification handling
#
class NotificationHandler(BaseNotificationHandler, actions.RequestAction):
    """Notification handler class for feed requests."""

    notification_template = (
        "geo_rdm_records/email/feed/request-package-publication.html",
    )
    """Notification template."""

    def _build_message(self, identity, **kwargs):
        """Message factory.

        Args:
            identity (flask_principal.Identity): Entity identity.

            **kwargs: Extra arguments

        Returns:
            dict: message metadata.
        """
        request_id = str(self.request.id)

        # Preparing package data to the notification
        package = self.request.topic.resolve()
        package_id = package["id"]

        record = current_geo_packages_service.read(identity, package_id).to_dict()

        package_title = record["metadata"]["title"]
        package_url = record["links"]["self_html"]

        # Preparing request data
        # Generating request ui address as the requests service doesn't generate it
        # ToDo: This should be a temporary solution
        _ui_url = current_app.config["SITE_UI_URL"]
        request_url = f"{_ui_url}/me/requests/{request_id}"

        notification_emails = current_app.config[
            "GEO_RDM_NOTIFICATION_DEFAULT_RECEIVER_EMAILS"
        ]

        if notification_emails:
            return dict(
                subject="[GEO Knowledge Hub] New Feed post request",
                template_html=self.notification_template,
                recipients=notification_emails,
                ctx=dict(
                    record_title=package_title,
                    record_url=package_url,
                    request=request_id,
                    request_url=request_url,
                ),
            )

    #
    # High-level API
    #
    def notify(self, identity, uow, **kwargs):
        """Notify users with a given message."""
        try:
            message = self._build_message(identity)
            super().notify(identity, message, uow)
        except NoResultFound:
            pass  # any notification is sent


#
# Actions
#
class SubmitAction(NotificationHandler, actions.SubmitAction):
    """Submit action.

    ToDos:
        - Submit action can send an e-mail to a pre-configured address (secretariat, admins, or receivers)
    """

    def execute(self, identity, uow):
        """Execute the submit action."""
        record = self.request.topic.resolve()
        # Create a custom title for the request
        record_title = record["metadata"]["title"]
        request_title = f"Feed: {record_title}"

        # Defining the custom title for the request
        self.request["title"] = request_title

        # Use the CMS service to manage the feed post.
        self.notify(identity, uow=uow)

        super().execute(identity, uow)


class AcceptAction(NotificationHandler, actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept feed post creation."""
        # Finish operation.
        super().execute(identity, uow)


#
# Request
#
class FeedPostRequest(RequestType):
    """Feed post creation request for a Knowledge Package.

    ToDos
        - Review the ``needs_context`` and how it can be used
    """

    type_id = "requests-assistance-feed-creation"
    name = _("Feed post creation")

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
