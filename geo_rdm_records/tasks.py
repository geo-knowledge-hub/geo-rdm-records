# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tasks module."""

from celery import shared_task
from invenio_rdm_records.records.models import RDMRecordMetadata as GEORecordMetadata

from geo_rdm_records import validation
from geo_rdm_records.modules.packages.records.models import GEOPackageRecordMetadata


@shared_task(ignore_result=True)
def check_records_links():
    """Check records links.

    ToDos:
        - Implement chunk system with multi worker support (one worker for each chunk)
    """
    # ToDo: Review the chunk size
    chunk_size = 25

    # Packages: validating links
    # ToDo: Include report function
    validation.check_links(
        GEOPackageRecordMetadata, chunk_size, validation.check_chunk_of_package, None
    )

    # Resources: validating links
    # ToDo: Include report function
    validation.check_links(
        GEORecordMetadata, chunk_size, validation.check_chunk_of_resources, None
    )
