# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Metadata schema definition."""

from invenio_rdm_records.services.schemas import MetadataSchema as BaseMetadataSchema
from invenio_rdm_records.services.schemas.metadata import VocabularySchema
from marshmallow import fields

from geo_rdm_records.modules.resources.services.schemas.location import FeatureSchema


class MetadataSchema(BaseMetadataSchema):
    """GEO Knowledge Hub Record Metadata field schema."""

    #
    # Locations
    #
    locations = fields.Nested(FeatureSchema)

    #
    # Target Audience
    #
    target_audiences = fields.List(fields.Nested(VocabularySchema))

    #
    # GEO Work Programme Activities
    #
    geo_work_programme_activity = fields.Nested(VocabularySchema)

    #
    # Engagement Priorities
    #
    engagement_priorities = fields.List(fields.Nested(VocabularySchema))
