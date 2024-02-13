# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resouces UI serializers module."""

from .schema import UIRecordSchema
from .serializer import UIJSONSerializer

__all__ = ("UIRecordSchema", "UIJSONSerializer")
