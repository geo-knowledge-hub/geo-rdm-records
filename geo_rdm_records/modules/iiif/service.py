# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records IIIF service."""

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.services import IIIFService as BaseIIIFService

from geo_rdm_records.proxies import (
    current_geo_packages_service,
    current_marketplace_service,
)


class IIIFService(BaseIIIFService):
    """IIIF service."""

    modes = {
        "record": ["record", "draft"],
        "package": ["package", "package-draft"],
        "marketplace": ["marketplace-item", "marketplace-item-draft"],
    }
    """Service operation mode."""

    modes_service = {
        "record": current_rdm_records_service,
        "package": current_geo_packages_service,
        "marketplace": current_marketplace_service,
    }
    """Service per mode."""

    modes_type = {
        "record": {"record": ["record"], "draft": ["draft"]},
        "package": {"record": ["package"], "draft": ["package-draft"]},
        "marketplace": {
            "record": ["marketplace-item"],
            "draft": ["marketplace-item-draft"],
        },
    }
    """Types handled in each operation mode."""

    def _get_mode(self, type_):
        """Get the operation mode of the service."""
        for mode in self.modes:
            if type_ in self.modes[mode]:
                return mode

    def _get_mode_type(self, type_):
        """Get the type handled by the operation of the service."""
        mode = self._get_mode(type_)
        mode_types = self.modes_type[mode]

        for mode_type in mode_types:
            if type_ in mode_types[mode_type]:
                return mode_type

    def _get_service(self, type_):
        """Get the subservice."""
        mode = self._get_mode(type_)
        return self.modes_service[mode]

    def file_service(self, type_):
        """Get the correct instance of the file service, draft vs record."""
        service = self._get_service(type_)
        mode_type = self._get_mode_type(type_)

        return service.files if mode_type == "record" else service.draft_files

    def read_record(self, identity, uuid):
        """Read the correct version of the record and its files."""
        type_, id_ = self._iiif_uuid(uuid)

        # Defining the operation mode of the service.
        service = self._get_service(type_)
        mode_type = self._get_mode_type(type_)

        read = service.read if mode_type == "record" else service.read_draft
        record = read(identity=identity, id_=id_)

        file_service = self.file_service(type_)
        files = file_service.list_files(identity=identity, id_=id_)

        record.files = files

        return record
