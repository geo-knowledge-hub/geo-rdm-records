# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Checker module."""

from urllib.parse import urlparse

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
    valid_schemes = ["http", "https"]
    record_links_status = []

    for link in record_links:
        link_tested = False
        link_is_available = False

        link_parse = urlparse(link)

        # currently, only http-https are tested
        if link_parse.scheme in valid_schemes:
            link_tested = True
            link_is_available = is_link_available(link, **kwargs)

        # testing `www` websites with no scheme
        elif link.startswith("www"):
            for valid_scheme in valid_schemes:
                if not link_is_available:
                    try:
                        link_with_scheme = urlparse(f"{valid_scheme}://{link}")
                        link_with_scheme = link_with_scheme.geturl()

                        link_is_available = is_link_available(
                            link_with_scheme, **kwargs
                        )

                        link_tested = True
                    except:  # noqa
                        pass

        record_links_status.append(
            dict(link=link, is_available=link_is_available, is_tested=link_tested)
        )

    return record_links_status


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
