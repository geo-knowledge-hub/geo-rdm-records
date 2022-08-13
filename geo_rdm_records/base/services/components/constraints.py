# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Service constraints."""

from invenio_drafts_resources.services.records.components import ServiceComponent


class ConstrainedComponent(ServiceComponent):
    """A constrained component is a subtype that can be used to validate user-defined data."""

    constraints = []
    """Constraints to be checked."""

    def validate(self, **kwargs):
        """Validate if the user-defined data follows the defined constraints."""
        for constraint in self.constraints:
            constraint.check(**kwargs)


class BaseComponentConstraint:
    """Base component constraint class.

    A constraint is used to compose the validation rules
    in a ``ConstrainedComponent`` class.

    The subclasses of this class **must** generate an exception when
    the constraint is not valid.
    """

    @classmethod
    def check(cls, **kwargs):
        """Check if the constraint is valid or not."""
        raise NotImplementedError("This method must be implemented.")
