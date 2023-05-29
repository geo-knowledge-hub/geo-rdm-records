# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records CMS service module."""

from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import TaskOp, unit_of_work

from geo_rdm_records.modules.cms.tasks import notify_feed


class CMSService(Service):
    """CMS Service."""

    @unit_of_work()
    def create_feed_post(self, identity, request, uow):
        """Create a feed post."""
        self.require_permission(identity, "accept_request")

        # Preparing data to create the notification task
        record = request.topic.resolve()

        request_id = str(request.id)
        record_id = str(record.pid.pid_value)

        # Sending notification e-mail
        uow.register(TaskOp(notify_feed, request_id, record_id))

        # ToDo: Improve this return to provide more
        #       details of the operation performed.
        return True
