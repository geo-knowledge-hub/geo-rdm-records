# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Validation Helper module."""

from flask import current_app


def get_retry_config(confvar: str = "GEO_RDM_CHECKER_RETRY_CONFIG"):
    """Helper to get configurations of retry."""
    return current_app.config[confvar]


def get_requests_config(confvar: str = "GEO_RDM_CHECKER_REQUEST_CONFIG"):
    """Helper to get configurations of the ``requests.get`` method."""
    return current_app.config[confvar]


def get_chunks_config(confvar: str = "GEO_RDM_CHECKER_CHUNK_SIZE"):
    """Helper to get configurations of the checker chunking system."""
    return current_app.config[confvar]


def get_sleep_config(confvar: str = "GEO_RDM_CHECKER_SLEEP_TIME"):
    """Helper to get configurations of the sleep time used between the chunks processing."""
    return current_app.config[confvar]


def create_checker_config():
    """Create configuration object for the Link Checker."""
    return dict(requests_config=get_requests_config(), retry_config=get_retry_config())
