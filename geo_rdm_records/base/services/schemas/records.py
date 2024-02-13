# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records schema."""


from invenio_rdm_records.services.schemas import RDMRecordSchema as BaseRecordSchema
from marshmallow_utils.fields import NestedAttribute

from geo_rdm_records.base.services.schemas import MetadataSchema, ParentSchema


class BaseGEORecordSchema(BaseRecordSchema):
    """Base GEO Records schema."""

    parent = NestedAttribute(ParentSchema)
    metadata = NestedAttribute(MetadataSchema)
