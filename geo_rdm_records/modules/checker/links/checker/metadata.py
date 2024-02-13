# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Checker metadata management module."""

import re

from pydash import py_


def _extract_links(record_document):
    """Extract all links from a string.

    Args:
        record_document (str): Record document as a string.

    Returns:
        list: List containing all links found in the record document.
    """
    # Regex pattern for extracting URLs
    url_pattern = r'https?://[^\s<>"\',]+|www\.[^\s<>"\',]+'

    # Find all non-overlapping matches of the pattern in the string
    return py_.map(re.findall(url_pattern, record_document), lambda x: x.strip(")."))


def extract_links_from_record(record):
    """Extract all links available in a record.

    Args:
        record (invenio_records.api.Record): Record object

    Returns:
        list: List containing all links found in the record document.
    """
    record_metadata_as_string = str(record.dumps())

    # Extracting links
    record_links = _extract_links(record_metadata_as_string)

    # Removing duplicates
    return py_.uniq(record_links)
