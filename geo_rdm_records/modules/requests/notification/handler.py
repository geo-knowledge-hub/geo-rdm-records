# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Notification handler."""

from pydash import py_

from geo_rdm_records.proxies import current_requests_notification_service


class BaseNotificationHandler:
    """Notification handler class."""

    #
    # Base API
    #
    def _notify(self, identity, message, uow, **kwargs):
        """Notify users with a given message."""
        # test if recipients are defined
        recipients = py_.get(message, "recipients")

        if recipients:
            current_requests_notification_service.notify(identity, message, uow=uow)

    #
    # High-level API
    #
    def notify(self, identity, messages, uow, **kwargs):
        """Notify users with a given message."""
        if isinstance(messages, list):
            for message in messages:
                self._notify(identity, message, uow, **kwargs)

        elif messages is not None:
            self._notify(identity, messages, uow, **kwargs)
