# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Validation tasks module."""

from celery import shared_task

from geo_rdm_records.modules.checker.links.service import config
from geo_rdm_records.modules.checker.links.validation import validate_records_links


@shared_task(ignore_result=True)
def check_records_links():
    """Check records links."""
    # reading configurations
    report_configuration = config.get_report_config()
    checker_configuration = config.get_checker_config()

    # validating links!
    validate_records_links(checker_configuration, report_configuration)
