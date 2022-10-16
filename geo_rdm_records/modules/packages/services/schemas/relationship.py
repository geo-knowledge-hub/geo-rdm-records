# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Relationship Schemas."""

from marshmallow import Schema, fields

from geo_rdm_records.base.services.schemas import RelationshipElementSchema


class RelationshipSchema(Schema):
    """Schema for the Record relationship."""

    # Managed resource
    resources = fields.List(fields.Nested(RelationshipElementSchema))
