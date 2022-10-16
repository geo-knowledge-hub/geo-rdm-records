# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI Serializer schema."""

from invenio_rdm_records.resources.serializers.ui.schema import (
    RelatedIdentifiersSchema as BaseRelatedIdentifiersSchema,
)
from invenio_rdm_records.resources.serializers.ui.schema import (
    UIRecordSchema as UIRecordSchemaBase,
)
from invenio_vocabularies.resources import VocabularyL10Schema
from marshmallow import fields


class RelatedIdentifiersSchema(BaseRelatedIdentifiersSchema):
    """Localization of language titles."""

    title = fields.String()

    description = fields.String()


class UIRecordSchema(UIRecordSchemaBase):
    """Schema for dumping extra information for the UI."""

    #
    # Base metadata
    #
    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifiersSchema()),
        attribute="metadata.related_identifiers",
    )

    #
    # Custom fields
    #
    geo_work_programme_activity = fields.Nested(
        VocabularyL10Schema, attribute="metadata.geo_work_programme_activity"
    )

    target_audiences = fields.List(
        fields.Nested(VocabularyL10Schema),
        attribute="metadata.target_audiences",
    )

    engagement_priorities = fields.List(
        fields.Nested(VocabularyL10Schema),
        attribute="metadata.engagement_priorities",
    )
