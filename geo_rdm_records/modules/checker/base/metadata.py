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
from geo_rdm_records.proxies import current_geo_packages_service


def expand_record_metadata(rid_, cache_, type_):
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
