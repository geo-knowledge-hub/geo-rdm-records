# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Funding schema definition."""

from invenio_rdm_records.services.schemas.metadata import (
    FundingSchema as BaseFundingSchema,
)
from invenio_vocabularies.contrib.awards.schema import (
    AwardRelationSchema as BaseAwardRelationSchema,
)
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class AwardRelationSchema(BaseAwardRelationSchema):
    """Award schema with support to icon and disclaimer."""

    # ToDo: Review this to limit use for specific cases (e.g., EU projects)
    icon = SanitizedUnicode(required=False)
    disclaimer = SanitizedUnicode(required=False)


class FundingSchema(BaseFundingSchema):
    """Funding schema."""

    award = fields.Nested(AwardRelationSchema)
