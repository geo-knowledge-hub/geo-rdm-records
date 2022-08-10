# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Schemas."""

from invenio_rdm_records.services.schemas import RDMRecordSchema as BaseRecordSchema
from marshmallow_utils.fields import NestedAttribute

from .relationship import RelationshipSchema


class GEOPackageRecordSchema(BaseRecordSchema):
    """Record schema."""

    relationship = NestedAttribute(RelationshipSchema)
