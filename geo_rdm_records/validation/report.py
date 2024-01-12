# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Validations report module."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_mail.api import TemplatedMessage
from invenio_users_resources.proxies import current_users_service


def _check_owner_can_receive_report(owner_profile):
    """Check if an owner can receive a report."""
    # Checking if user can receive emails. To receive an email, user
    # must have the following properties:
    #   1. Must be `Active`;
    #   2. Must have `Email` confirmed.
    is_active = owner_profile["active"]
    is_email_confirmed = owner_profile["confirmed"]

    return is_active and is_email_confirmed


def _build_report_message(
    records, records_owner_profile, report_title, report_template
):
    """Build the report message."""
    # formatting the user e-mail.
    records_owner_email = [records_owner_profile["email"]]

    return TemplatedMessage(
        subject=report_title,
        template_html=report_template,
        recipients=records_owner_email,
        ctx={**records},
    )


def send_report(records, records_owner):
    """Send a report to Knowledge Provider."""
    report_base_title = "GEO Knowledge Hub - Links status from your records"
    report_base_template = "geo_rdm_records/reports/records-report.html"

    # reading owner profile
    owner_profile = current_users_service.read(system_identity, records_owner).to_dict()

    # checking if the owner can receive a report
    can_receive_report = _check_owner_can_receive_report(owner_profile)

    if can_receive_report:
        # building the message
        report_message = _build_report_message(
            records, owner_profile, report_base_title, report_base_template
        )

        # sending the message
        current_app.extensions["mail"].send(report_message)
