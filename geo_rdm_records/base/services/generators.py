# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permissions generators module."""

from invenio_rdm_records.services.generators import ConditionalGenerator

from geo_rdm_records.modules.packages.records.api import GEOPackageRecord


class IfPackage(ConditionalGenerator):
    """Generator that depends on whether the record is a package or not.

    IfPackage(
        then_=[...],
        else_=[...]
    )
    """

    def _condition(self, record, **kwargs):
        """Check if the record is a package."""
        return isinstance(record, GEOPackageRecord)
