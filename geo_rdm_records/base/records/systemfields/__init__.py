# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base System Fields components for the GEO RDM Records."""

from .common import BaseGEORecordsFieldsMixin
from .proxy import BaseRecordProxy, BaseRecordsProxy
from .relationship import BaseRelationshipField

__all__ = (
    "BaseGEORecordsFieldsMixin",
    "BaseRelationshipField",
    "BaseRecordProxy",
    "BaseRecordsProxy",
)
