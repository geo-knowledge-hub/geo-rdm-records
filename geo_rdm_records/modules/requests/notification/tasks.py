# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records tasks."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_mail.api import TemplatedMessage

from geo_rdm_records.proxies import current_geo_packages_service


#
# Tasks
#
@shared_task
def notify_request(
    request_id,
    record_id,
    notification_template="geo_rdm_records/email/notification.html",
):
    """Create a notification about a new request."""
    # Preparing package data to the notification
    record = current_geo_packages_service.read(system_identity, record_id).to_dict()

    package_title = record["metadata"]["title"]
    package_url = record["links"]["self_html"]

    # Preparing request data
    # Generating request ui address as the requests service doesn't generate it
    # ToDo: This should be a temporary solution
    _ui_url = current_app.config["SITE_UI_URL"]
    request_url = f"{_ui_url}/me/requests/{request_id}"

    # Getting e-mails to be notified (initial implementation)
    # ToDo: Groups must be used in a future version
    notification_emails = current_app.config[
        "GEO_RDM_NOTIFICATION_DEFAULT_RECEIVER_EMAILS"
    ]

    if notification_emails:
        # Preparing notification
        message = TemplatedMessage(
            subject="GEO Knowledge Hub: New request",
            template_html=notification_template,
            recipients=notification_emails,
            ctx=dict(
                record_title=package_title,
                record_url=package_url,
                request=request_id,
                request_url=request_url,
            ),
        )

        # Sending notification
        current_app.extensions["mail"].send(message)
