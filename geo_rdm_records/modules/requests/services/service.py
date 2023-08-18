# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records CMS service module."""

from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import TaskOp, unit_of_work

from geo_rdm_records.modules.requests.tasks import notify_request


class AssistanceRequestsService(Service):
    """Assistance requests Service."""

    @unit_of_work()
    def create_request(self, identity, request, uow):
        """Create an assistance request."""
        self.require_permission(identity, "accept_request")

        # Preparing data to create the notification task
        record = request.topic.resolve()

        request_id = str(request.id)
        record_id = str(record.pid.pid_value)

        # Sending e-mail notification
        uow.register(TaskOp(notify_request, request_id, record_id))

        # ToDo: Improve this return to provide more
        #       details of the operation performed.
        return True
