# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tasks module."""

from time import sleep

from invenio_links_checker import checker_validate_links
from invenio_links_checker.contrib.chunking import checker_create_chunks_by_owners
from invenio_rdm_records.records.models import RDMRecordMetadata as GEORecordMetadata

from geo_rdm_records.customizations.records.api import GEORecord
from geo_rdm_records.modules.packages.records.api import GEOPackageRecord
from geo_rdm_records.modules.packages.records.models import GEOPackageRecordMetadata
from geo_rdm_records.validation import config, report
from geo_rdm_records.validation.records import enrich_status_objects


def _check_chunk_packages(packages):
    """Check links from chunks of Knowledge Packages."""
    results = []

    # reading checker configuration
    checker_configuration = config.create_checker_config()

    for package in packages:
        package = GEOPackageRecord.get_record(package.id)

        package_is_latest = package.versions.is_latest
        package_is_published = package.is_published

        # Check only the latest versions of published packages
        if package_is_latest and package_is_published:
            # Extracting resources
            package_resources = [r.resolve() for r in package.relationship.resources]

            # Validating links from resources
            package_resources_links_status = checker_validate_links(package_resources)

            # Validating links from the package
            package_links_status = checker_validate_links(
                [package], **checker_configuration
            )

            # Saving the result
            results.append(
                dict(
                    package=package_links_status[0],
                    resources=package_resources_links_status,
                )
            )

    return results


def _check_chunk_resources(resources):
    """Check links from chunks of resources."""
    valid_resources = []

    # reading checker configuration
    checker_configuration = config.create_checker_config()

    for resource in resources:
        resource = GEORecord.get_record(resource.id)

        resource_is_published = resource.is_published
        resource_is_latest = resource.versions.is_latest
        resource_is_managed = resource.parent.relationship.managed_by is None

        # select only the latest versions of not-managed published resources
        if resource_is_latest and resource_is_published and resource_is_managed:
            valid_resources.append(resource)

    return checker_validate_links(valid_resources, **checker_configuration)


def _check_chunk(record_chunk):
    """Check links of the records in the chunk.

    Note:
        In the GEO Knowledge Hub case, it is required to group the records by type and then validate them.
    """
    # filtering the records by type.
    packages = list(filter(lambda x: x.parent.json["type"] == "package", record_chunk))
    resources = list(filter(lambda x: x.parent.json["type"] != "package", record_chunk))

    # validating the links.
    return [*_check_chunk_packages(packages), *_check_chunk_resources(resources)]


def check_links(chunk_size):
    """Check links from any type of InvenioRDM records."""
    # reading configurations
    sleep_time = config.get_sleep_config()

    # loading records
    resources = GEORecordMetadata.query.all()
    records = GEOPackageRecordMetadata.query.all()

    records.extend(resources)

    # creating chunks
    chunks = checker_create_chunks_by_owners(records, chunk_size)

    # validating chunks
    for chunk in chunks:
        chunk_owner = chunk["owner"]
        chunk_records = chunk["records"]

        chunk_results = _check_chunk(chunk_records)
        chunk_results = enrich_status_objects(chunk_results)

        report.send_report(chunk_results, chunk_owner)

        # note: In the GEO Knowledge Hub case, it is possible to stop between
        #       chunks as we don't have a lot of resources. In other cases, another approach
        #       should be considered.
        if sleep_time:
            sleep(sleep_time)
