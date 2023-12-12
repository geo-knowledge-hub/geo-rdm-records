# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tasks module."""

from invenio_links_checker import checker_validate_links
from invenio_links_checker.contrib.chunking import checker_create_chunks

from geo_rdm_records.customizations.records.api import GEORecord
from geo_rdm_records.modules.packages.records.api import GEOPackageRecord


def check_chunk_of_package(packages):
    """Check links from chunks of Knowledge Packages."""
    results = []

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
            package_links_status = checker_validate_links([package])

            # Saving the result
            results.append(
                dict(
                    package=package_links_status[0],
                    resources=package_resources_links_status,
                )
            )

    return results


def check_chunk_of_resources(resources):
    """Check links from chunks of resources."""
    valid_resources = []

    for resource in resources:
        resource = GEORecord.get_record(resource.id)

        resource_is_published = resource.is_published
        resource_is_latest = resource.versions.is_latest
        resource_is_managed = resource.parent.relationship.managed_by is None

        # Select only the latest versions of not-managed published resources
        if resource_is_latest and resource_is_published and resource_is_managed:
            valid_resources.append(resource)

    checker_validate_links(valid_resources)


def check_links(metadata_cls, chunk_size, chunk_validation_fnc, report_fnc):
    """Check links from any type of InvenioRDM records."""
    # Loading records
    records = metadata_cls.query.all()

    # Creating chunks
    records_chunks = checker_create_chunks(records, chunk_size)

    # Validating chunks
    for record_chunk in records_chunks:
        chunk_results = chunk_validation_fnc(record_chunk)

        # ToDo: Create report
        # for chunk_result in chunk_results:
        #   report_fnc(chunk_result)
