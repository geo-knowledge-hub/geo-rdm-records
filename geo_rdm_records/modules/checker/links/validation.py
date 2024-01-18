# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Validation links module."""

from invenio_access.models import User
from invenio_search.engine import dsl

from geo_rdm_records.modules.checker.base import records as checker_records
from geo_rdm_records.modules.checker.base import report as checker_reports
from geo_rdm_records.modules.checker.links import records as record_utils
from geo_rdm_records.modules.checker.links.checker import check


def _validate_packages_links(packages, checker_configuration):
    """Validate links from Knowledge Packages.

    Args:
        packages (list): List of ``GEOPackageRecord``.

        checker_configuration (dict): Extra configurations for the link checker.

    Returns:
        list: List containing status of the links from the packages.
    """
    results = []

    for package in packages:
        package_is_latest = package.versions.is_latest
        package_is_published = package.is_published

        # Check only the latest versions of published packages
        if package_is_latest and package_is_published:
            # Extracting resources
            package_resources = [r.resolve() for r in package.relationship.resources]

            # Validating links from resources
            package_resources_links_status = check.checker_validate_links(
                package_resources
            )

            # Validating links from the package
            package_links_status = check.checker_validate_links(
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


def _validate_resources_links(resources, checker_configuration):
    """Validate links from Knowledge Resources.

    Args:
        resources (list): List of ``GEORecord``

        checker_configuration (dict): Extra configurations for the link checker.

    Returns:
        list: List containing status of the links from the resources.
    """
    valid_resources = []

    for resource in resources:
        resource_is_published = resource.is_published
        resource_is_latest = resource.versions.is_latest
        resource_is_managed = resource.parent.relationship.managed_by is None

        # select only the latest versions of not-managed published resources
        if resource_is_latest and resource_is_published and resource_is_managed:
            valid_resources.append(resource)

    return check.checker_validate_links(valid_resources, **checker_configuration)


def _validate_records_links(records, checker_configuration):
    """Check links from records (Knowledge Packages and Knowledge Resources).

    Args:
        records (list): List of ``GEOPackageRecord`` and ``GEORecord``.

        checker_configuration (dict): Extra configurations for the link checker.

    Returns:
        list: List containing status of the links from the records.
    """
    # filtering the records by type.
    packages = list(filter(lambda x: x.parent["type"] == "package", records))
    resources = list(filter(lambda x: x.parent["type"] != "package", records))

    # validating the links.
    return [
        *_validate_packages_links(packages, checker_configuration),
        *_validate_resources_links(resources, checker_configuration),
    ]


def validate_records_links(checker_configuration, report_configuration):
    """Validate links from GEO Knowledge Hub records (Knowledge Packages and Knowledge Resources)."""
    for user in User.query.yield_per(1000):
        records_owner_id = user.id

        # reading records associated with the current author (packages and resources)
        records_obj, records_metadata = checker_records.get_records_by_owner(
            records_owner_id, extra_filter=dsl.Q("term", **{"versions.is_latest": True})
        )

        if not len(records_obj):
            continue

        # checking links
        validation_results = _validate_records_links(records_obj, checker_configuration)
        validation_results = record_utils.enrich_results(
            validation_results, metadata_cache=records_metadata
        )

        # reporting results
        checker_reports.send_report(
            validation_results, records_owner_id, report_configuration
        )
