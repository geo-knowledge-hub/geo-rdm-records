# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API errors."""

from flask_babelex import lazy_gettext as _


class PackageError(Exception):
    """Base Package error class."""


class InvalidPackageError(PackageError):
    """Package invalid error."""


class InvalidPackageResourceError(PackageError):
    """Resource package invalid error."""


class InvalidRelationshipError(PackageError):
    """Relationship is not valid for the package/resource defined."""


class PackageRequestException(PackageError):
    """Base class for Knowledge Packages request errors."""


class PackageRequestNotFoundError(PackageError):
    """Review was not found for the selected package."""

    def __init__(self, *args, **kwargs):
        """Initializer."""
        super().__init__(_("Review not found."), *args, **kwargs)
