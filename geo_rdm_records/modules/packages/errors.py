# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API errors."""


class PackageError(Exception):
    """Base Package error class."""


class InvalidPackageResourceError(PackageError):
    """Resource package invalid error."""


class InvalidRelationshipError(PackageError):
    """Relationship is not valid for the package/resource defined."""
