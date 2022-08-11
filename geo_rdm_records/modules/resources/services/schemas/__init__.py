# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services schema."""

from invenio_rdm_records.services.schemas import RDMRecordSchema
from marshmallow_utils.fields import NestedAttribute

from geo_rdm_records.modules.resources.services.schemas.metadata import MetadataSchema


class GEORecordSchema(RDMRecordSchema):
    """GEO Knowledge Hub Record Schema."""

    metadata = NestedAttribute(MetadataSchema)
