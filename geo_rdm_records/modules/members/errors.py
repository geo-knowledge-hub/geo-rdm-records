# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Members API errors."""

from ..packages.errors import PackageError


class AlreadyMemberError(PackageError):
    """Exception raised when entity is already a member or already invited.

    Note:
        Implemented based on ``AlreadyMemberError`` from the Invenio Communities.
    """


class InvalidMemberError(PackageError):
    """Error raised when a member is invalid.

    Note:
        For instance a user/group cannot be found, or is not allowed to be added.

    Note:
        Implemented based on ``InvalidMemberError`` from the Invenio Communities.
    """
