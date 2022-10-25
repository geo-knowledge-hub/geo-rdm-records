# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record links for the Packages API."""

from invenio_records_resources.services.base import Link


class RecordLink(Link):
    """Shortcut for writing record links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URL template."""
        vars.update(
            {"id": record.pid.pid_value, "parent_id": record.parent.pid.pid_value}
        )
