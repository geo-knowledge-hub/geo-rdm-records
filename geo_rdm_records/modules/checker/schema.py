# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schema module."""

from flask_resources import BaseObjectSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer
from invenio_vocabularies.resources import VocabularyL10Schema
from marshmallow import fields


class EmailRecordSchema(BaseObjectSchema):
    """Record schema for e-mails."""

    resource_type = fields.Nested(
        VocabularyL10Schema, attribute="metadata.resource_type"
    )


class EmailRecordJSONSerializer(MarshmallowSerializer):
    """Record serializer for e-mails."""

    def __init__(self):
        """Initializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=EmailRecordSchema,
            schema_context={"object_key": "ui"},
        )
