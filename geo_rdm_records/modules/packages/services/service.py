# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Services."""

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.services import (
    RDMRecordService as BaseRDMRecordService,
)
from invenio_records_resources.services import ServiceSchemaWrapper
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)
from sqlalchemy.orm.exc import NoResultFound

from ..errors import InvalidPackageResourceError
from ..records.api import PackageRelationship
from .schemas.resources import ResourcesSchema


class GEOPackageRecordService(BaseRDMRecordService):
    """GEO Package record service."""

    #
    # Properties
    #
    @property
    def resource_cls(self):
        """Resource record class."""
        return self.config.resource_cls

    @property
    def resource_draft_cls(self):
        """Resource draft class."""
        return self.config.resource_draft_cls

    @property
    def resource_schema(self):
        """Schema for resource definition."""
        return ServiceSchemaWrapper(self, schema=ResourcesSchema)

    #
    # Internal methods
    #
    def _handle_resources(self, identity, id_, data, revision_id, action, uow, expand):
        # reproducibility/consistency requirement: users can only add/remove
        # resources from draft packages.
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # concurrency control
        self.check_revision_id(draft, revision_id)

        # permissions
        self.require_permission(identity, "update_draft", record=draft)

        # Load data with service schema
        data, errors = self.resource_schema.load(data, context={"identity": identity})

        resources = data["resources"]

        for resource in resources:
            resource_obj = None
            resource_id = resource["id"]
            relationship_type = resource["type"]

            # defining the rule to load a resource based on
            # the relationship type:
            #   - ``related``: Can't be loaded as a draft;
            #   - ``managed``: Must be loaded as a draft.
            allow_draft = not (relationship_type == PackageRelationship.RELATED.value)

            # for both ``Published`` and ``Draft`` records it is assumed
            # that the permission verification is done in a specialized
            # constrained component. This is done because this verification
            # is combined with other properties of the record.
            try:
                resource_obj = self.resource_cls.pid.resolve(
                    resource_id, registered_only=False
                )

            except NoResultFound as e:
                if not allow_draft:
                    raise InvalidPackageResourceError(resource) from e

                resource_obj = self.resource_draft_cls.pid.resolve(
                    resource_id, registered_only=False
                )

            # running the components to link the package and resources
            self.run_components(
                action,
                identity,
                record=draft,
                resource=resource_obj,
                relationship_type=relationship_type,
            )

            # Commit and index (only in bidirectional connections) where
            # modifications are made in the resource.
            if relationship_type == PackageRelationship.MANAGED.value:
                for r in draft.relationship.managed:
                    record_resource = r.resolve()  # cached

                    # assuming that the package/resource integration
                    # only uses the ``parent``.
                    uow.register(RecordCommitOp(record_resource.parent))
                    uow.register(
                        RecordIndexOp(
                            record_resource, indexer=current_rdm_records_service.indexer
                        )
                    )

        # Commit and index
        uow.register(RecordCommitOp(draft, self.indexer))

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            errors=errors,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    #
    # Resources handling
    #
    @unit_of_work()
    def resource_add(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk add resources in a package."""
        action = "package_add_resource"
        return self._handle_resources(
            identity, id_, data, revision_id, action, uow, expand
        )

    @unit_of_work()
    def resource_delete(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk delete resources from a package."""
        action = "package_delete_resource"
        return self._handle_resources(
            identity, id_, data, revision_id, action, uow, expand
        )

    @unit_of_work()
    def resource_update(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk update resources from a package."""
        action = "package_update_resource"
        return self._handle_resources(
            identity, id_, data, revision_id, action, uow, expand
        )
