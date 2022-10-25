# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Views decorators."""

from functools import wraps

from flask import g
from invenio_pidstore.errors import PIDUnregistered
from sqlalchemy.exc import NoResultFound

from geo_rdm_records.base.resources.serializers import UIRecordJSONSerializer
from geo_rdm_records.proxies import current_geo_packages_service


def get_package_service():
    """Return the current package service."""
    return current_geo_packages_service


def pass_package_or_draft(serialize):
    """Retrieve package (record or draft)."""

    def decorator(f):
        @wraps(f)
        def view(**kwargs):
            service = get_package_service()

            identity = g.identity
            pid_value = kwargs["pid_value"]

            try:
                package = service.read(identity=identity, id_=pid_value)
            except (NoResultFound, PIDUnregistered):
                package = service.read_draft(identity=identity, id_=pid_value)

            kwargs["package"] = package
            if serialize:
                package_ui = UIRecordJSONSerializer().dump_obj(package.to_dict())
                kwargs["package_ui"] = package_ui

            return f(**kwargs)

        return view

    return decorator
