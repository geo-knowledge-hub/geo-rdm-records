# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Modules."""

from importlib import import_module

from geo_rdm_records.class_factory import ClassFactory

MODULES = [
    "geo_rdm_records.customizations",
    "geo_rdm_records.modules.packages",
    # "geo_rdm_records.modules.members",
]

# initializing models
for module in MODULES:
    mod = import_module(module)
    mod.init_class(ClassFactory)
