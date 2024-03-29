# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API integration."""

from geo_rdm_records.modules.packages.records.api import GEOPackageDraft
from geo_rdm_records.modules.rdm.records.api import GEODraft, GEORecord


def test_package_integration_with_resources(
    db, running_app, minimal_package, minimal_record, es_clear
):
    """Basic smoke test for packages integration."""

    # Creating the package and the resource
    package_draft = GEOPackageDraft.create(minimal_package)
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
    package_draft.relationship.resources.add(resource_draft)
    package_draft.relationship.resources.add(resource_record)

    package_draft.commit()
    db.session.commit()

    # Linking the package with the resource
    resource_record.parent.relationship.managed_by = package_draft.parent

    # Checking the package relationship
    assert len(package_draft.relationship.resources) == 1

    # Checking the record relationship
    assert resource_record.parent.relationship.dump() == dict(
        managed_by={"id": package_draft.parent.pid.pid_value}
    )

    # Removing and checking again
    package_draft.relationship.resources.remove(resource_record)

    assert len(package_draft.relationship.resources) == 0
