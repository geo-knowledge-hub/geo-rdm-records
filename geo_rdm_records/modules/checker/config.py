# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration utility module."""

from flask import current_app


def get_links_checker_config():
    """Get configuration object for the Link Checker."""
    # Retry
    retry_config = current_app.config["GEO_RDM_CHECKER_LINKS_RETRY_CONFIG"]

    # Requests
    requests_config = current_app.config["GEO_RDM_CHECKER_LINKS_REQUEST_CONFIG"]

    return dict(requests_config=requests_config, retry_config=retry_config)


def get_outdated_records_checker_config():
    """Get configuration object for the Record Checker."""
    # Outdated criteria
    outdated_criteria = current_app.config["GEO_RDM_CHECKER_OUTDATED_CRITERIA"]

    return dict(
        outdated_criteria=outdated_criteria,
    )


def get_links_report_config():
    """Get configuration object for links status report."""
    # report template configuration
    report_template = "geo_rdm_records/reports/links-status-report.html"

    # report title configuration
    report_title = current_app.config["GEO_RDM_CHECKER_LINKS_REPORT_TITLE"]

    return dict(report_title=report_title, report_template=report_template)


def get_outdated_report_config():
    """Get configuration object for outdated records report."""
    # report template configuration
    report_template = "geo_rdm_records/reports/outdated-records-report.html"

    # report title configuration
    report_title = current_app.config["GEO_RDM_CHECKER_OUTDATED_REPORT_TITLE"]

    return dict(report_title=report_title, report_template=report_template)
