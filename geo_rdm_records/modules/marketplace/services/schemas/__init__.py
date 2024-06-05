# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Services schemas."""

from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode

from geo_rdm_records.base.services.schemas import MetadataSchema as BaseMetadataSchema
from geo_rdm_records.base.services.schemas.records import BaseGEORecordSchema


#
# Metadata
#
class MarketplaceFields(Schema):
    """Fields for marketplace object."""

    launch_url = SanitizedUnicode(required=True, validate=validate.URL())

    vendor_contact = SanitizedUnicode(required=True, validate=validate.Email())


class MetadataSchema(BaseMetadataSchema):
    """Metadata schema for marketplace items."""

    marketplace = fields.Nested(MarketplaceFields, required=True)


#
# Marketplace item
#
class GEOMarketplaceItemSchema(BaseGEORecordSchema):
    """Marketplace item metadata."""

    metadata = NestedAttribute(MetadataSchema)
