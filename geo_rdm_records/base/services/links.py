# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search links."""

from copy import deepcopy

from invenio_records_resources.services.base.links import (
    LinksTemplate as BaseLinksTemplate,
)

from geo_rdm_records.customizations.records.api import GEODraft, GEORecord
from geo_rdm_records.modules.marketplace.records.api import (
    GEOMarketplaceItem,
    GEOMarketplaceItemDraft,
)
from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)


class LinksRegistryType:
    """Registry types for mutable links."""

    supported_types = {
        "records": (
            GEODraft,
            GEORecord,
        ),
        "packages": (
            GEOPackageDraft,
            GEOPackageRecord,
        ),
        "marketplace-items": (
            GEOMarketplaceItemDraft,
            GEOMarketplaceItem,
        ),
    }

    @classmethod
    def guess_type(cls, obj, error=True):
        """Guess object type based on the types available."""
        for key in cls.supported_types.keys():
            if isinstance(obj, cls.supported_types.get(key)):
                return key

        if error:
            raise RuntimeError("Not able to mutate the link: Type not supported")


class MutableLinksTemplate(BaseLinksTemplate):
    """Templates for generating links for an object."""

    def __init__(self, links, types_registry, context=None):
        """Initializer."""
        super().__init__(links, context)

        self.types_registry = types_registry

    def expand(self, identity, obj):
        """Expand all the link templates."""
        # defining the object type
        obj_type = self.types_registry.guess_type(obj, error=True)

        # updating the context with the type
        ctx = deepcopy(self.context)
        ctx.update(dict(entity=obj_type, identity=identity))

        # expanding links
        links = {}

        for key, link in self._links.items():
            if link.should_render(obj, ctx):
                links[key] = link.expand(obj, ctx)
        return links
