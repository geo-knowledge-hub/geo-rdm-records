# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages Resources API."""

from geo_rdm_records.class_factory import init_class_factory

from .records.api import GEODraft, GEORecord


def init_class(factory):
    """Register the models in the Class Factory."""
    factory_classes = [
        GEODraft,
        GEORecord,
    ]

    init_class_factory(factory, factory_classes)
