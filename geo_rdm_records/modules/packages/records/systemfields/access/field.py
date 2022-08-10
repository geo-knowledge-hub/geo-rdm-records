# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Access system field."""

from invenio_rdm_records.records.systemfields.access.field.parent import (
    ParentRecordAccessField as BaseParentRecordAccessField,
)

from .parent import ParentRecordAccess


class ParentRecordAccessField(BaseParentRecordAccessField):
    """System field for managing record access."""

    def __init__(self, key="access", access_obj_class=ParentRecordAccess):
        """Create a new ParentRecordAccessField instance."""
        super().__init__(key=key, access_obj_class=access_obj_class)
