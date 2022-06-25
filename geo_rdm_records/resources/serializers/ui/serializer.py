# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resouces serializers."""


from invenio_rdm_records.resources.serializers.ui import (
    UIJSONSerializer as UIJSONSerializerBase,
)

from geo_rdm_records.resources.serializers.ui.schema import UIRecordSchema


#
# Serializer
#
class UIJSONSerializer(UIJSONSerializerBase):
    """UI JSON Serializer."""

    object_schema_cls = UIRecordSchema
