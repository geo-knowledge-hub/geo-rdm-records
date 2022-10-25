# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.services.uow import RecordCommitOp, RecordIndexOp

from geo_rdm_records.modules.packages.records.api import PackageRelationship


class PackageResourceAccessComponent(ServiceComponent):
    """Component to validate and integrate packages and resources access."""

    def package_add_resource(
        self, identity, package=None, resource=None, relationship_type=None, **kwargs
    ):
        """Add resource to a package."""
        if relationship_type == PackageRelationship.MANAGED.value:
            package_access = package.get("access", {})
            resource_access = resource.get("access", {})

            if package_access.get("record") == "restricted":
                # We only copy the entire package access when it is 'restricted'.
                # this is because, when a package is private, all resources associated
                # with it must be private to.
                resource.access = package_access

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler."""
        new_access_obj = data["access"]

        if new_access_obj["record"] == "restricted":
            for resource in record.relationship.resources:
                resource_obj = resource.resolve()

                # Modifications must be made only in resources managed by the
                # package.
                resource_manager = resource_obj.parent.relationship.managed_by or None

                if resource_manager:
                    if resource_manager.pid.pid_value == record.parent.pid.pid_value:
                        # preparing the access object
                        if not resource_obj.is_published:
                            # We must not change published resources! So, in
                            # this case, we do nothing when we find one.
                            resource_access = resource_obj.access.dump()
                            resource_access.update(
                                dict(
                                    record=new_access_obj.get("record"),
                                    embargo=new_access_obj.get("embargo"),
                                )
                            )

                            resource_obj.access = resource_access

                            # Registering the modifications
                            self.uow.register(RecordCommitOp(resource_obj))
                            self.uow.register(
                                RecordIndexOp(
                                    resource_obj,
                                    indexer=current_rdm_records_service.indexer,
                                )
                            )
