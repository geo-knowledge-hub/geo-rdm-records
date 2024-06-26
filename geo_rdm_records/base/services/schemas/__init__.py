# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services schemas."""

from .harvester import HarvesterSchema
from .location import FeatureSchema
from .metadata import MetadataSchema
from .parent import ParentSchema
from .relationship import RelationshipElementSchema

__all__ = (
    "FeatureSchema",
    "MetadataSchema",
    "ParentSchema",
    "RelationshipElementSchema",
    "HarvesterSchema",
)
