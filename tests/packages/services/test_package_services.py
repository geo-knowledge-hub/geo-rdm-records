# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Services."""

from geo_rdm_records.proxies import current_geo_packages_service


def test_minimal_draft_creation(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity

    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["resource_type"] == {
        "id": "image-photo",
        "title": {"en": "Photo"},
    }


def test_draft_w_languages_creation(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    minimal_record["metadata"]["languages"] = [
        {
            "id": "eng",
        }
    ]

    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["languages"] == [
        {"id": "eng", "title": {"en": "English", "da": "Engelsk"}}
    ]
