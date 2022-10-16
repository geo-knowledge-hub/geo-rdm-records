# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI Schema for the GEO RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from .schema.ui.record import UIRecordSchema


class UIRecordJSONSerializer(MarshmallowSerializer):
    """UI JSON serializer for GEO RDM Records classes."""

    def __init__(self):
        """Initializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIRecordSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )
