# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Secret Links Services."""

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.secret_links.service import (
    SecretLinkService as BaseSecretLinkService,
)
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work

from .service import get_context_manager


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
        package, _ = self.get_parent_and_record_or_draft(id_)

        # Use the same link to the resources.
        for resource in package.relationship.resources:
            resource = resource.resolve()

            # ToDo: In the first approach of the Packages API, the relations are classified
            #       Now, this classification is implicit and must be checked all the time.
            #       In a future version, we need to validate if this is the best approach
            #       or test a "classified" relation, where the relations are internally
            #       classified with a "type" tag.
            resource_manager = get_context_manager(resource)

            if resource_manager["id"] == package.parent["id"]:
                # ToDo: (Temporary solution) The previous links are replaced
                #       by the package links.
                resource.parent.access.links.clear()
                resource.parent.access.links.extend(package.parent.access.links)

                uow.register(RecordCommitOp(resource.parent))
                uow.register(
                    RecordCommitOp(
                        resource,
                        indexer=current_rdm_records_service.indexer,
                        index_refresh=True,
                    )
                )

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
