# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode

from invenio_rdm_records.services.schemas.parent import (
    RDMParentSchema as BaseParentSchema,
)


class ParentSchema(BaseParentSchema):
    """Record Parent schema."""

    knowledge_packages = fields.List(SanitizedUnicode(required=True))
