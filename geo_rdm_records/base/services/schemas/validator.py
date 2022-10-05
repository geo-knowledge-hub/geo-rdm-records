# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services schemas."""


from marshmallow.validate import ValidationError, Validator


class ResourceType(Validator):
    """Validator which succeeds if the value passed to it represents a specific resource type.

    ToDo:
        Check if Invenio already have a solution for validations like this.
    """

    def __init__(self, resource_type_id):
        """Initializer."""
        self._resource_type_id = resource_type_id

    def __call__(self, value):
        """Call method."""
        if value.get("id") != self._resource_type_id:
            raise ValidationError("Invalid resource type!")

        return value
