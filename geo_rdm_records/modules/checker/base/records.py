# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records manipulation utility module."""

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service

from geo_rdm_records.modules.packages.records.api import GEOPackageRecord
from geo_rdm_records.modules.rdm.records.api import GEORecord
from geo_rdm_records.proxies import current_geo_packages_service


def get_records_by_owner(owner_id, **kwargs):
    """Get all records associated with an owner.

    Args:
        owner_id (int): Owner ID

        **kwargs (dict): Extra parameters for the services search methods.

    Returns:
        tuple: Tuple containing a list of records and its metadata.
    """
    search_params = {"q": f"parent.access.owned_by.user: {owner_id}"}

    # searching all records (packages and resources) and its metadata
    packages_metadata = list(
        current_geo_packages_service.search(
            system_identity, params=search_params, **kwargs
        ).hits
    )

    resources_metadata = list(
        current_rdm_records_service.search(
            system_identity, params=search_params, **kwargs
        ).hits
    )

    # reading reference from database
    records_obj = [
        *list(map(lambda x: GEOPackageRecord.pid.resolve(x["id"]), packages_metadata)),
        *list(map(lambda x: GEORecord.pid.resolve(x["id"]), resources_metadata)),
    ]

    return records_obj, dict(packages=packages_metadata, resources=resources_metadata)
