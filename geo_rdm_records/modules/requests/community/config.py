# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community-related requests."""

from invenio_requests.customizations import actions

from geo_rdm_records.modules.requests.community.submission import (
    AcceptAction,
    CancelAction,
    DeclineAction,
    ExpireAction,
    SubmitAction,
)

#
# Extra configurations for the `CommunitySubmission` class
#   > This configuration is possible as in the GEO Knowledge Hub, we use a
#   > custom version of the `CommunitySubmission` class, which has support for
#   > `overridable configurations.`
#
CommunitySubmissionConfig = {
    "allowed_topic_ref_types": ["record", "package", "marketplace_item"],
    "available_actions": {
        "create": actions.CreateAction,
        "submit": SubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "cancel": CancelAction,
        "decline": DeclineAction,
        "expire": ExpireAction,
    },
}
