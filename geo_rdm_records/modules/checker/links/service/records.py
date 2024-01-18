# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records manipulation utility module."""

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service

from geo_rdm_records.base.records.types import GEORecordTypes
from geo_rdm_records.customizations.records.api import GEORecord
from geo_rdm_records.modules.checker.schema import EmailRecordJSONSerializer
from geo_rdm_records.modules.packages.records.api import GEOPackageRecord
from geo_rdm_records.proxies import current_geo_packages_service


#
# Utilities
#
def _calculate_links(record):
    """Calculate the number of links.

    Args:
        record (dict): Dict containing links associated with a record.
    Returns:
        int: Number of links available in the given record.
    """
    return len(list(record["links_status"]))


def _calculate_links_with_errors(record):
    """Calculate the number of links with errors.

    Args:
        record (dict): Dict containing links associated with a record.

    Returns:
        int: Number of links with an error.
    """
    return len(list(filter(lambda x: not x["is_available"], record["links_status"])))


def _summarize_records_total(packages, resources):
    """Summarize total number of records (packages and resources).

    Args:
        packages (list): List of packages

        resources (list): List of individual resources (not associated with packages).
    Returns:
        int: Total number of records.
    """
    nrecords = len(resources)

    for package in packages:
        # 1 package + n resources
        nrecords += 1 + len(package["resources"])

    return nrecords


def _summarize(records, key):
    """Summarize total number of objects in a given key.

    Args:
        records (list): List of dict

        key (str): Key to be checked from each record in ``records``
    Returns:
        int: Number of objects available in the given key.
    """
    return sum(map(lambda x: x[key], records))


def _serialize_record(record):
    """Serialize record.

    Args:
        record (dict): Record (Package or resource) with metadata to be serialized.

    Returns:
        dict: Record with serialized fields.
    """
    return EmailRecordJSONSerializer().dump_obj(record)


def _enrich_resource(resource):
    """Enrich a link status object from a resource.

    Args:
        resource (dict): Record metadata to be enriched.
    Returns:
        dict: Record enriched.
    """
    resource_obj = _serialize_record(resource)

    nlinks = _calculate_links(resource)
    nerrors = _calculate_links_with_errors(resource)

    return {
        **resource,
        "metadata": resource_obj["metadata"],
        "ui": resource_obj["ui"],
        "owners": resource_obj["parent"]["access"]["owned_by"],
        "nerrors": nerrors,
        "nlinks": nlinks,
    }


def _enrich_package(package):
    """Enrich a link status object from a resource.

    Args:
        package (dict): Record metadata to be enriched.
    Returns:
        dict: Record enriched.
    """
    # processing the package
    package_obj = _serialize_record(package["package"])

    nlinks = _calculate_links(package["package"])
    nerrors = _calculate_links_with_errors(package["package"])

    package_result = {
        **package["package"],
        "metadata": package_obj["metadata"],
        "ui": package_obj["ui"],
        "owners": package_obj["parent"]["access"]["owned_by"],
        "errors": nerrors,
        "nlinks": nlinks,
    }

    # processing resources
    resources_result = []
    package_resources = package["resources"]

    for resource in package_resources:
        resource = _enrich_resource(resource)
        resources_result.append(resource)

        nlinks += resource["nlinks"]
        nerrors += resource["nerrors"]

    return dict(
        package=package_result,
        resources=resources_result,
        nerrors=nerrors,
        nlinks=nlinks,
    )


def _read_record_metadata(rid_, cache_, type_):
    """Read metadata of a record.

    Args:
        rid_ (str): Record ID.

        cache_ (dict): Dict containing already loaded metadata.

        type_ (str): Type of record.

    Returns:
        dict: Record metadata.
    """
    result_data = list(filter(lambda x: x["id"] == rid_, cache_))

    if not result_data:
        if type_ == GEORecordTypes.package:
            result_data = current_geo_packages_service.read(
                identity=system_identity, id_=rid_
            ).to_dict()

        else:
            result_data = current_rdm_records_service.read(
                identity=system_identity, id_=rid_
            ).to_dict()

    else:
        result_data = result_data[0]

    return result_data


def _merge_metadata(records, cache):
    """Merge metadata inside record link status objects.

    Args:
        records (list): List containing links status objects.

        cache (dict): Dict with already loaded metadata from packages and resources.

    Yields:
        dict: Record metadata object.
    """
    for record in records:
        if "package" in record:
            # preparing package metadata
            package_metadata = _read_record_metadata(
                record["package"]["id"], cache["packages"], GEORecordTypes.package
            )
            package_metadata = {**record["package"], **package_metadata}

            # preparing resources metadata
            resources_metadata = []

            for resource in record["resources"]:
                resource_metadata = _read_record_metadata(
                    resource["id"], cache["resources"], GEORecordTypes.resource
                )

                resources_metadata.append({**resource, **resource_metadata})

            yield dict(package=package_metadata, resources=resources_metadata)

        else:
            individual_resource_metadata = _read_record_metadata(
                record["id"], cache["resources"], GEORecordTypes.resource
            )

            yield {**record, **individual_resource_metadata}


#
# Records high-level functions.
#
def enrich_status_objects(records_status_object, metadata_cache):
    """Inject extra metadata in the links status object.

    Args:
        records_status_object (list): List of record status link object.

        metadata_cache (dict): Already loaded metadata.

    Returns:
        list: Records with extra metadata.
    """
    packages = []
    resources = []

    # first, we merge status objects with the metadata already available
    records_status_object = _merge_metadata(records_status_object, metadata_cache)

    for record_status_object in records_status_object:
        record_is_package = True if "package" in record_status_object else False

        if record_is_package:
            packages.append(_enrich_package(record_status_object))
        else:
            resources.append(_enrich_resource(record_status_object))

    # summarizing some metrics
    number_of_records = _summarize_records_total(packages, resources)
    number_of_errors = _summarize(packages, "nerrors") + _summarize(
        resources, "nerrors"
    )

    packages_links = _summarize(packages, "nlinks")
    resources_links = _summarize(resources, "nlinks")

    return dict(
        packages=packages,
        resources=resources,
        total_errors=number_of_errors,
        total_records=number_of_records,
        total_packages_links=packages_links,
        total_resources_links=resources_links,
    )


def get_records_by_owner(owner_id):
    """Get all records associated with an owner.

    Args:
        owner_id (int): Owner ID

    Returns:
        tuple: Tuple containing a list of records and its metadata.
    """
    search_params = {"q": f"parent.access.owned_by.user: {owner_id}"}

    # searching all records (packages and resources) and its metadata
    packages_metadata = list(
        current_geo_packages_service.search(system_identity, params=search_params).hits
    )

    resources_metadata = list(
        current_rdm_records_service.search(system_identity, params=search_params).hits
    )

    # reading reference from database
    records_obj = [
        *list(map(lambda x: GEOPackageRecord.pid.resolve(x["id"]), packages_metadata)),
        *list(map(lambda x: GEORecord.pid.resolve(x["id"]), resources_metadata)),
    ]

    return records_obj, dict(packages=packages_metadata, resources=resources_metadata)
