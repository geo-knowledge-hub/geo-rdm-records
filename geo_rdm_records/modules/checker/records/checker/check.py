# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Check module."""


import datetime


def _is_outdated(record, threshold):
    """Check if a record is outdated."""
    date_threshold = datetime.datetime.now() - datetime.timedelta(threshold)

    return not (record["last_update"] > date_threshold)


def check_records_outdated(records, date_threshold=6 * 365 / 12):
    """Check which record is outdated.

    Args:
        records (list): List of dicts containing the records and their last update dates.

        date_threshold (number): Number of days used as threshold (6 months by default).

    Returns:
        list: List of dicts containing records and flags indicating if they are outdated.
    """
    for record in records:
        record["is_outdated"] = _is_outdated(record, date_threshold)

    return records
