# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records CMS service module."""

from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import TaskOp, unit_of_work

from geo_rdm_records.modules.requests.notification.tasks import notify_request


class RequestNotificationService(Service):
    """Requests notification Service.

    Note:
        - This service will be removed in the next version of the Invenio RDM (v12).
    """

    @unit_of_work()
    def notify(self, identity, message, uow):
        """Request notification."""
        # Sending e-mail notification
        uow.register(TaskOp(notify_request, message))

        # ToDo: Improve this return to provide more
        #       details of the operation performed.
        return True
