# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API integration."""

from geo_rdm_records.modules.packages.records.api import GEOPackageDraft
from geo_rdm_records.records.api import GEODraft, GEORecord


def test_package_integration_with_resources(db, running_app, minimal_record):
    """Basic smoke test for packages integration."""

    # Creating the package and the resource
    package_draft = GEOPackageDraft.create(minimal_record)
    resource_draft = GEODraft.create(minimal_record)

    # Committing both package and resource
    package_draft.commit()
    resource_draft.commit()

    db.session.commit()

    # Creating a resource record
    resource_record = GEORecord.publish(resource_draft)
    resource_record.commit()

    db.session.commit()

    # Linking the resource with the package
    package_draft.relationship.managed_resources.add(resource_record)
    package_draft.relationship.managed_resources.add(
        resource_record
    )  # only one must be added.

    package_draft.relationship.related_resources.add(resource_record)

    package_draft.commit()
    db.session.commit()

    # Checking the relationship
    assert len(package_draft.relationship.managed_resources) == 1
    assert len(package_draft.relationship.related_resources) == 1
