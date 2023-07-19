# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records feed post requests."""

from flask_babelex import lazy_gettext as _
from invenio_requests.customizations import RequestType, actions

from geo_rdm_records.proxies import current_cms_service


#
# Actions
#
class SubmitAction(actions.SubmitAction):
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
        super().execute(identity, uow)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept feed post creation."""
        # Use the CMS service to manage the feed post.
        current_cms_service.create_feed_post(identity, self.request, uow=uow)

        # Finish operation.
        super().execute(identity, uow)


#
# Request
#
class FeedPostRequest(RequestType):
    """Feed post creation request for a Knowledge Package."""

    type_id = "feed-post-creation"
    name = _("Feed post creation")

    creator_can_be_none = False
    topic_can_be_none = False

    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["geo_package_record"]

    available_actions = {
        "create": actions.CreateAction,
        "submit": SubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "cancel": actions.CreateAction,
        "decline": actions.DeclineAction,
        "expire": actions.ExpireAction,
    }
