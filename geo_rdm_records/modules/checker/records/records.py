# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records manipulation utility module."""

from geo_rdm_records.base.records.types import GEORecordTypes
from geo_rdm_records.modules.checker.base import metadata as checker_metadata
from geo_rdm_records.modules.checker.base import stats as checker_stats
from geo_rdm_records.modules.checker.schema import EmailRecordJSONSerializer


#
# Utilities
#
def _count(records, key):
    """Count valid values into a list of dicts.

    Args:
        records (list): Records (Package or resource).

        key (str): Key to be access in each record.

    Returns:
        int: Number of valid values inside ``key``
    """
    return len(list(filter(lambda x: x[key], records)))


def _serialize_record(record):
    """Serialize record.

    Args:
        record (dict): Record (Package or resource) with metadata to be serialized.

    Returns:
        dict: Record with serialized fields.
    """
    return EmailRecordJSONSerializer().dump_obj(record)


#
# Records high-level functions.
#
def get_update_date_from_records(records):
    """Get last update date from records.

    Args:
        records (list): List of records (Package or resource).

    Returns:
        list: List of dicts containing the records and their last update dates.
    """
    records_update_dates = []

    for record in records:
        if record.parent.type == GEORecordTypes.package:
            package_update_dates = [record.updated]

            for resource in record.relationship.resources:
                package_update_dates.append(resource.resolve().updated)

            # checking the minimum date
            last_update_date = min(package_update_dates)

            records_update_dates.append(
                dict(
                    record=record,
                    last_update=last_update_date,
                    type=GEORecordTypes.package,
                )
            )

        else:
            if record.parent.relationship.managed_by is None:
                records_update_dates.append(
                    dict(
                        record=record,
                        last_update=record.updated,
                        type=GEORecordTypes.resource,
                    )
                )

    return records_update_dates


def enrich_results(results, metadata_cache):
    """Inject extra metadata in the links status object.

    Args:
        results (list): List of records from date validation.

        metadata_cache (dict): Already loaded metadata.

    Returns:
        dict: Records with extra metadata.
    """
    packages = []
    resources = []

    for result in results:
        if result["type"] == GEORecordTypes.package:
            result["record"] = _serialize_record(
                checker_metadata.expand_record_metadata(
                    result["record"]["id"],
                    metadata_cache["packages"],
                    GEORecordTypes.package,
                )
            )

            packages.append(result)

        else:
            result["record"] = _serialize_record(
                checker_metadata.expand_record_metadata(
                    result["record"]["id"],
                    metadata_cache["resources"],
                    GEORecordTypes.resource,
                )
            )

            resources.append(result)

    # calculating metrics
    number_of_records = checker_stats.count_records(**metadata_cache)
    number_of_packages_outdated = _count(packages, "is_outdated")
    number_of_resources_outdated = _count(resources, "is_outdated")

    return dict(
        packages=packages,
        resources=resources,
        total_records=number_of_records,
        total_packages_outdated=number_of_packages_outdated,
        total_resources_outdated=number_of_resources_outdated,
    )
