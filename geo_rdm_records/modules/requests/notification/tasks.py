# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records tasks."""

from celery import shared_task
from flask import current_app
from invenio_mail.api import TemplatedMessage


#
# Tasks
#
@shared_task
def notify_request(message):
    """Create a notification about a new request."""
    if isinstance(message, dict):
        message = TemplatedMessage(**message)

    current_app.extensions["mail"].send(message)
