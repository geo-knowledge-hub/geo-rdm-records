# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Config conditional generators."""

from abc import ABC, abstractmethod
from itertools import chain

from invenio_records.dictutils import dict_lookup
from invenio_records_permissions.generators import Generator


class BaseConditionalGenerator(ABC, Generator):
    """Base generator to enable the creation of conditional generators."""

    @abstractmethod
    def generators(self, **kwargs):
        """Choose between 'then' or 'else' generators."""

    def needs(self, **kwargs):
        """Needs to grant permission."""
        # in the chain above is checked if the
        # ``g`` has ``needs``. In this case is assumed
        # that ``g`` is a ``Generator``. Otherwise, is
        # assumed that ``g`` is a ``flask_principal.Need``.
        return set(
            chain.from_iterable(
                [
                    g.needs(**kwargs) if hasattr(g, "needs") else [g]
                    for g in self.generators(**kwargs)
                ]
            )
        )

    def excludes(self, **kwargs):
        """Needs to grant permission."""
        return set(
            chain.from_iterable(
                [
                    g.excludes(**kwargs) if hasattr(g, "needs") else [g]
                    for g in self.generators(**kwargs)
                ]
            )
        )


class IfIsEqual(BaseConditionalGenerator):
    """IfIsEqual generator.

    This conditional generator check if a record attribute is equal a defined value:
        IfIsEqual(
            field    = 'data.status',
            equal_to = 'A',
            then_    = [<Generator>, <Generator>,],
            else_    = [<Generator>, <Generator>,]
        )
    Note:
        The ideia and base implementation of the conditional generators is presented in the
        Invenio-RDM-Records, so, thanks invenio team for this.
    """

    def __init__(self, field, equal_to, then_, else_):
        """Initializer."""
        self.field = field
        self.then_ = then_
        self.else_ = else_

        self.equal_to = equal_to

    def generators(self, record=None, **kwargs):
        """Choose between 'then' or 'else' generators."""
        if record is None:
            return self.else_

        # Handling properties and keys equally
        try:
            value = dict_lookup(record, self.field)
        except KeyError:
            value = getattr(record, self.field)

        if value == self.equal_to:
            return self.then_
        return self.else_
