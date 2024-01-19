# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Checker module."""

from .metadata import extract_links_from_record
from .network import is_link_available


def _check_links(record_links, **kwargs):
    """Check links from a given record.

    Args:
        record_links (list): List of links from a given record.

        **kwargs: Extra configurations for the `is_link_available` function.

    Returns:
        list: List with the links' status.
    """
    return [
        dict(link=link, is_available=is_link_available(link, **kwargs))
        for link in record_links
    ]


def checker_validate_links(records, **kwargs):
    """Check links from records.

    Args:
        records (list): List of ``invenio_records.api.Record`` objects.

        **kwargs: Extra configurations for the `is_link_available` function.

    Returns:
        list: List with the links' status.
    """
    result = []

    for record in records:
        record_id = record.pid.pid_value

        # extracting the links and checking its status
        record_links = extract_links_from_record(record)
        record_links_status = _check_links(record_links, **kwargs)

        result.append(dict(id=record_id, links_status=record_links_status))

    return result
