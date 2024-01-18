# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration utility module."""

from flask import current_app


def _get_retry_config(confvar: str = "GEO_RDM_CHECKER_RETRY_CONFIG"):
    """Get configurations of retry."""
    return current_app.config[confvar]


def _get_requests_config(confvar: str = "GEO_RDM_CHECKER_REQUEST_CONFIG"):
    """Get configurations of the ``requests.get`` method."""
    return current_app.config[confvar]


def _get_report_title(confvar: str = "GEO_RDM_CHECKER_REPORT_TITLE"):
    """Get configurations of the sleep time used between the chunks processing."""
    return current_app.config[confvar]


def _get_report_template(confvar: str = "GEO_RDM_CHECKER_REPORT_TEMPLATE"):
    """Get configurations of the sleep time used between the chunks processing."""
    return current_app.config[confvar]


def get_checker_config():
    """Get configuration object for the Link Checker."""
    return dict(
        requests_config=_get_requests_config(), retry_config=_get_retry_config()
    )


def get_report_config():
    """Get configuration object for the Report."""
    return dict(
        report_title=_get_report_title(), report_template=_get_report_template()
    )
