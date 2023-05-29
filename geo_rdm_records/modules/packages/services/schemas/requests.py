# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Assistance Requests Schemas."""

from marshmallow import Schema, fields


class RequestSchema(Schema):
    """Request schema."""

    id = fields.UUID()

    type = fields.Str()
    status = fields.Str()
