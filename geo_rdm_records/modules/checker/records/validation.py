# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Validation records module."""

from invenio_access.models import User
from invenio_search.engine import dsl

from geo_rdm_records.modules.checker.base import records as checker_records
from geo_rdm_records.modules.checker.base import report as checker_reports
from geo_rdm_records.modules.checker.records import records as record_utils
from geo_rdm_records.modules.checker.records.checker import check


def validate_records_outdated(outdated_criteria_configuration, report_configuration):
    """Validate outdated records."""
    for user in User.query.yield_per(1000):
        records_owner_id = user.id

        records_obj, records_metadata = checker_records.get_records_by_owner(
            records_owner_id, extra_filter=dsl.Q("term", **{"versions.is_latest": True})
        )

        if not len(records_obj):
            continue

        records_dates = record_utils.get_update_date_from_records(records_obj)

        # checking what are the outdated packages
        records_dates = check.check_records_outdated(
            records_dates, outdated_criteria_configuration["outdated_criteria"]
        )
        records_dates = record_utils.enrich_results(records_dates, records_metadata)

        # reporting results
        checker_reports.send_report(
            records_dates, records_owner_id, report_configuration
        )
