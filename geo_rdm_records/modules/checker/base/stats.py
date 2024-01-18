# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Stats for checkers."""


def count_records(packages, resources):
    """Count total number of records (packages and resources).

    Args:
        packages (list): List of packages

        resources (list): List of individual resources (not associated with packages).
    Returns:
        int: Total number of records.
    """
    return len(packages) + len(resources)
