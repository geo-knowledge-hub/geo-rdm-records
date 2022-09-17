# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service errors."""

from flask_babelex import lazy_gettext as _
from invenio_rdm_records.services.errors import ReviewException


class ReviewInconsistentResourceRestrictions(ReviewException):
    """Check if the resource is associated with a Knowledge Package."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(
            _(
                "Record resources associated with a package can't be related to a community directly"
            ),
            *args,
            **kwargs,
        )
