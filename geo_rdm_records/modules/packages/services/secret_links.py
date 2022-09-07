# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Secret Links Services."""

from copy import copy

from invenio_rdm_records.services.secret_links.service import (
    SecretLinkService as BaseSecretLinkService,
)
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work


class SecretLinkService(BaseSecretLinkService):
    """GEO RDM Secret Link service."""

    def _op_proxy(self, id_, uow):
        """Proxy method to handle package secret links.

        Note:
            We have implemented this method to avoid code duplication with the
            Invenio RDM Team. Our main goal here is to add a tailored-rule for
            package management.

            We're still investigating if this is the best approach to handle package
            and resources.

        Note:
            Some known issues:
                - If a given package have many resources, maybe, the initial implementation
                can be a problem, once we need to iterate and update all of them before
                publish the package.
        """
        record, _ = self.get_parent_and_record_or_draft(id_)

        # Use the same link to the resources.
        for resource in record.relationship.managed_resources:
            resource = resource.resolve()

            resource.parent.access.links = copy(record.parent.access.links)

            uow.register(RecordCommitOp(resource.parent))
            uow.register(RecordCommitOp(resource))

            self._index_related_records(resource, resource.parent, uow=uow)

    @unit_of_work()
    def create(self, identity, id_, data, links_config=None, uow=None):
        """Create a secret link for a record (resp. its parent)."""
        # running the operation
        op_result = super().create(
            identity, id_, data, links_config=links_config, uow=uow
        )

        # proxying to handle rules for packages.
        self._op_proxy(id_, uow)

        return op_result

    @unit_of_work()
    def update(
        self,
        identity,
        id_,
        link_id,
        data,
        links_config=None,
        uow=None,
    ):
        """Update a secret link for a record (resp. its parent)."""
        # running the operation
        op_result = super().update(
            identity, id_, link_id, data, links_config=links_config, uow=uow
        )

        # proxying to handle rules for packages.
        self._op_proxy(id_, uow)

        return op_result

    @unit_of_work()
    def delete(self, identity, id_, link_id, links_config=None, uow=None):
        """Delete a secret link for a record (resp. its parent)."""
        # running the operation
        op_result = super().delete(
            identity, id_, link_id, links_config=links_config, uow=uow
        )

        # proxying to handle rules for packages.
        self._op_proxy(id_, uow)

        return op_result
