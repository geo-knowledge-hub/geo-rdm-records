# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records blog post requests."""

from flask_babelex import lazy_gettext as _
from invenio_requests.customizations import RequestType, actions


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
        request_title = f"Blog post: {record_title}"
        # Defining the custom title for the request
        self.request["title"] = request_title
        super().execute(identity, uow)


#
# Request
#
class BlogPostCreation(RequestType):
    """Blog post creation request for a Knowledge Package.

    ToDos
        - Review the ``needs_context`` and how it can be used
    """

    type_id = "blog-post-creation"
    name = _("Blog post creation")

    creator_can_be_none = False
    topic_can_be_none = False

    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["package_record"]

    available_actions = {
        "create": actions.CreateAction,
        "submit": SubmitAction,
        "delete": actions.DeleteAction,
        "accept": actions.AcceptAction,
        "cancel": actions.CreateAction,
        "decline": actions.DeclineAction,
        "expire": actions.ExpireAction,
    }
