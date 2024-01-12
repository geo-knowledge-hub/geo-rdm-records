# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record manipulation module."""

from geo_rdm_records.customizations.records.api import GEORecord
from geo_rdm_records.modules.packages.records.api import GEOPackageRecord


def _calculate_links(record):
    """Calculate the number of links."""
    return len(list(record["links_status"]))


def _calculate_links_with_errors(record):
    """Calculate the number of links with errors."""
    return len(list(filter(lambda x: not x["is_available"], record["links_status"])))


def _summarize_records_total(packages, resources):
    """Summarize total number of records (packages and resources)."""
    nrecords = len(resources)

    for package in packages:
        # 1 package + n resources
        nrecords += 1 + len(package["resources"])

    return nrecords


def _summarize(records, key):
    """Summarize total number of links errors (from packages and resources)."""
    return sum(map(lambda x: x[key], records))


def _enrich_resource(resource):
    """Load metadata from a resource object."""
    resource_obj = GEORecord.pid.resolve(resource["id"])

    nlinks = _calculate_links(resource)
    nerrors = _calculate_links_with_errors(resource)

    return {
        **resource,
        "metadata": resource_obj["metadata"],
        "owners": resource_obj.parent["access"]["owned_by"],
        "errors": nerrors,
        "links": nlinks,
    }


def _enrich_package(package):
    """Load metadata from a package object."""
    # processing the package
    package_obj = GEOPackageRecord.pid.resolve(package["package"]["id"])

    nlinks = _calculate_links(package["package"])
    nerrors = _calculate_links_with_errors(package["package"])

    package_result = {
        **package["package"],
        "metadata": package_obj["metadata"],
        "owners": package_obj.parent["access"]["owned_by"],
        "errors": nerrors,
        "links": nlinks,
    }

    # processing resources
    resources_result = []
    package_resources = package["resources"]

    for resource in package_resources:
        resource = _enrich_resource(resource)
        resources_result.append(resource)

        nlinks += resource["links"]
        nerrors += resource["errors"]

    return dict(
        package=package_result, resources=resources_result, errors=nerrors, links=nlinks
    )


def enrich_status_objects(records):
    """Inject extra metadata in the links status object."""
    packages = []
    resources = []

    for record in records:
        record_is_package = True if "package" in record else False

        if record_is_package:
            packages.append(_enrich_package(record))
        else:
            resources.append(_enrich_resource(record))

    # summarizing some metrics
    number_of_records = _summarize_records_total(packages, resources)
    number_of_errors = _summarize(packages, "errors") + _summarize(resources, "errors")

    packages_links = _summarize(packages, "links")
    resources_links = _summarize(resources, "links")

    return dict(
        packages=packages,
        resources=resources,
        total_errors=number_of_errors,
        total_records=number_of_records,
        total_packages_links=packages_links,
        total_resources_links=resources_links,
    )
