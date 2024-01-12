# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Validation tasks module."""

from celery import shared_task

from geo_rdm_records.validation.config import get_chunks_config
from geo_rdm_records.validation.links import check_links


@shared_task(ignore_result=True)
def check_records_links():
    """Check records links."""
    chunk_size = get_chunks_config()

    # validating links of packages and resources.
    check_links(chunk_size)
