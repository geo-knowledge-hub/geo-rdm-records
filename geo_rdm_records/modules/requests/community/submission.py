# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Community submission."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_records_resources.services.uow import RecordCommitOp, RecordIndexOp
from invenio_requests.customizations import actions
from invenio_users_resources.proxies import current_users_service
from pydash import py_
from sqlalchemy.exc import NoResultFound

from geo_rdm_records.modules.requests.notification.handler import (
    BaseNotificationHandler,
)
from geo_rdm_records.modules.requests.services import ServiceHandler


#
# Submission notification handler
#
class SubmissionNotificationHandler(
    BaseNotificationHandler, actions.RequestAction, ServiceHandler
):
    """Submission notification handler."""

    community_valid_roles = ["owner", "curator", "manager"]
    """Valid roles to receive e-mails related to the submission."""

    notification_name = None
    """Notification name."""

    notification_template = {
        "owner": None,
        "curator": None,
        "user": None,
        "system": None,
    }
    """Notification template."""

    #
    # Base API
    #
    def _get_notification_template(self, role):
        """Get notification template based on user's role."""
        return self.notification_template.get(role)

    def _recipients(self, identity=None, **kwargs):
        """Build list of email recipients."""
        # extract community users
        # system identity is used because this is an internal task designed to
        # inform all users associated with the community.
        community_id = str(self.request.receiver.resolve().id)
        community_users = current_communities.service.members.search(
            system_identity, community_id
        ).to_dict()

        # get community users
        community_users = py_.get(community_users, "hits.hits", [])
        community_users = py_.filter(
            community_users, lambda x: x["role"] in self.community_valid_roles
        )
        community_users = py_.map(
            community_users, lambda x: dict(id=int(x["member"]["id"]), role=x["role"])
        )

        # get record owner users
        record = self.request.topic.resolve()

        record_owners = record.parent.access.owned_by
        record_owners = py_.map(
            record_owners, lambda x: dict(id=x.resolve().id, role="user")
        )

        users = py_.concat(community_users, record_owners)
        users = py_.uniq_by(users, "id")

        # get emails (beyond the e-mails from the owner / requester, as default, configurable e-mails are also used)
        community_user_emails = (
            current_app.config["GEO_RDM_NOTIFICATION_DEFAULT_RECEIVER_EMAILS"] or []
        )

        community_user_emails = py_.map(
            community_user_emails,
            lambda x: dict(
                email=x,
                template=self._get_notification_template("system"),
                type="system",
            ),
        )

        for user in users:
            user_id = py_.get(user, "id")

            if not user_id:
                continue

            try:
                user_obj = current_users_service.read(
                    system_identity, user_id
                ).to_dict()

                user_email = py_.get(user_obj, "email")
                user_role = py_.get(user, "role")

                user_template = self._get_notification_template(user_role)

                if user_email and user_template:
                    community_user_emails.append(
                        dict(email=user_email, template=user_template, type="user")
                    )

            except:  # noqa
                pass

        # remove duplicates
        return py_.uniq_by(community_user_emails, "email")

    def _build_messages(self, identity=None, notification_type=None, **kwargs):
        """Message factory.

        Args:
            identity (flask_principal.Identity): Entity identity.

            notification_type (str): Notification type / name

            **kwargs: Extra arguments

        Returns:
            list: List with messages metadata.
        """
        """Build notification message."""
        # ToDo: Inject this configuration using the service configuration.
        _ui_url = current_app.config["SITE_UI_URL"]

        # get record and it's service
        record = self.request.topic.resolve()
        service = self._get_service(record)

        # define method
        read_method_fnc = service.read
        if record.is_draft:
            read_method_fnc = service.read_draft

        # get information from the record
        record_id = record["id"]
        record = read_method_fnc(system_identity, record_id).to_dict()

        record_title = record["metadata"]["title"]
        record_url = record["links"]["self_html"]

        # get information from request
        request_id = str(self.request.id)
        request_url = f"{_ui_url}/me/requests/{request_id}"

        # get receiver metadata
        receiver_title = py_.get(self.request.receiver.resolve(), "metadata.title")

        # recipients (user and system)
        recipients = self._recipients()

        recipients_user = py_.filter(recipients, lambda x: x["type"] == "user")
        recipients_system = py_.map(
            py_.filter(recipients, lambda x: x["type"] == "system"), "email"
        )

        # generate messages
        messages = []
        for recipient in recipients_user:
            recipient_email = recipient.get("email")
            recipient_template = recipient.get("template")

            if recipient_email and recipient_template:
                messages.append(
                    dict(
                        subject=f"[GEO Knowledge Hub] Community: {notification_type} - {record_title}",
                        template_html=recipient_template,
                        recipients=[recipient_email],
                        bcc=recipients_system,
                        ctx=dict(
                            record_title=record_title,
                            record_url=record_url,
                            request=request_id,
                            request_url=request_url,
                            community_name=receiver_title,
                        ),
                    )
                )

        return messages

    #
    # High-level API
    #
    def notify(self, identity, uow, notification_type, **kwargs):
        """Notify users with a given message."""
        try:
            messages = self._build_messages(
                identity, notification_type=notification_type
            )
            super().notify(identity, messages, uow)
        except NoResultFound:
            pass  # any notification is sent


#
# Actions
#
class SubmitAction(SubmissionNotificationHandler, actions.SubmitAction):
    """Submit action."""

    notification_name = "New review request"
    """Notification name."""

    notification_template = {
        "owner": "geo_rdm_records/email/community/request-submit-curator.html",
        "curator": "geo_rdm_records/email/community/request-submit-curator.html",
        "user": "geo_rdm_records/email/community/request-submit-user.html",
        "system": "geo_rdm_records/email/community/request-submit-curator.html",
    }
    """Notification template."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        # define the service
        draft = self.request.topic.resolve()
        service = self._get_service(draft)

        # validate record
        service._validate_draft(identity, draft)

        # Set the record's title as the request title.
        self.request["title"] = draft.metadata["title"]

        # Send notification
        self.notify(identity, uow, notification_type=self.notification_name)

        # execute!
        super().execute(identity, uow)


class AcceptAction(SubmissionNotificationHandler, actions.AcceptAction):
    """Accept action."""

    notification_name = "Record approved"
    """Notification name."""

    notification_template = {
        "owner": "geo_rdm_records/email/community/request-accept-curator.html",
        "curator": "geo_rdm_records/email/community/request-accept-curator.html",
        "user": "geo_rdm_records/email/community/request-accept-user.html",
        "system": "geo_rdm_records/email/community/request-accept-curator.html",
    }
    """Notification template."""

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
        # TODO: Ensure that the accepting user has permissions to publish.
        service.publish(identity, draft.pid.pid_value, uow=uow)

        # Send notification
        self.notify(identity, uow, notification_type=self.notification_name)

        super().execute(identity, uow)


class DeclineAction(SubmissionNotificationHandler, actions.DeclineAction):
    """Decline action."""

    notification_name = "Record denied"
    """Notification name."""

    notification_template = {
        "owner": "geo_rdm_records/email/community/request-deny-curator.html",
        "curator": "geo_rdm_records/email/community/request-deny-curator.html",
        "user": "geo_rdm_records/email/community/request-deny-user.html",
        "system": "geo_rdm_records/email/community/request-deny-curator.html",
    }
    """Notification template."""

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

        # Send notification
        self.notify(identity, uow, notification_type=self.notification_name)


class CancelAction(SubmissionNotificationHandler, actions.CancelAction):
    """Decline action."""

    notification_name = "Review canceled"
    """Notification name."""

    notification_template = {
        "owner": "geo_rdm_records/email/community/request-cancel-curator.html",
        "curator": "geo_rdm_records/email/community/request-cancel-curator.html",
        "user": "geo_rdm_records/email/community/request-cancel-user.html",
        "system": "geo_rdm_records/email/community/request-cancel-curator.html",
    }
    """Notification template."""

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

        # Send notification
        self.notify(identity, uow, notification_type=self.notification_name)


class ExpireAction(SubmissionNotificationHandler, actions.CancelAction):
    """Expire action."""

    notification_name = "Review expired"
    """Notification name."""

    notification_template = {
        "owner": "geo_rdm_records/email/community/request-expire.html",
        "curator": "geo_rdm_records/email/community/request-expire.html",
        "user": "geo_rdm_records/email/community/request-expire.html",
        "system": "geo_rdm_records/email/community/request-expire.html",
    }
    """Notification template."""

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

        self.notify(identity, uow, notification_type=self.notification_name)
