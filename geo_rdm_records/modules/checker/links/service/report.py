# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Report utility module."""

from datetime import datetime

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_mail.api import TemplatedMessage
from invenio_users_resources.proxies import current_users_service


def _check_owner_can_receive_report(owner_profile):
    """Check if an owner can receive a report.

    Args:
        owner_profile (dict): Dict containing owner profile.

    Returns:
        bool: Flag indicating if a given owner can receive e-mails.
    """
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
    """Build a report message.

    Args:
        records (list): List containing status of the links from the
                        records (Knowledge Packages and Knowledge Resources).

        records_owner_profile (dict): Dict with the profile of the records' owner.

        report_title (str): Report's e-mails title.

        report_template (str): Report's e-mails template.

    Returns:
        invenio_mail.api.TemplatedMessage: Email message.
    """
    # formatting the user e-mail.
    records_owner_email = [records_owner_profile["email"]]

    report_date = datetime.now().strftime("%B %d, %Y")

    return TemplatedMessage(
        subject=report_title,
        template_html=report_template,
        recipients=records_owner_email,
        ctx={**records, "report_date": report_date},
    )


def send_report(records, records_owner, report_configuration):
    """Send a report to Knowledge Provider.

    Args:
        records (list): List containing status of the links from the
                        records (Knowledge Packages and Knowledge Resources).

        records_owner (int): Record owner's ID.

        report_configuration (dict): Report configuration
    """
    # reading owner profile
    owner_profile = current_users_service.read(system_identity, records_owner).to_dict()

    # checking if the owner can receive a report
    can_receive_report = _check_owner_can_receive_report(owner_profile)

    if can_receive_report:
        # building the message
        report_message = _build_report_message(
            records, owner_profile, **report_configuration
        )

        # sending the message
        current_app.extensions["mail"].send(report_message)
