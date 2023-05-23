# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API External PIDs component."""

from copy import copy

from invenio_rdm_records.services.components import PIDsComponent as BasePIDsComponent
from invenio_records_resources.services.uow import TaskOp

from ..tasks import register_or_update_pid


class PIDsComponent(BasePIDsComponent):
    """External PIDs component for Packages."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        # ATTENTION: A draft can be for both an unpublished or published
        # record. For an unpublished record, we usually simply need to create
        # and reserve all PIDs. For a published record, some PIDs may allow
        # changes.

        # Extract all PIDs/schemes from the draft and the record
        draft_pids = draft.get("pids", {})
        record_pids = copy(record.get("pids", {}))
        draft_schemes = set(draft_pids.keys())
        record_schemes = set(record_pids.keys())
        required_schemes = set(self.service.config.pids_required)

        # Validate the draft PIDs
        self.service.pids.pid_manager.validate(draft_pids, record, raise_errors=True)

        # Detect which PIDs on a published record that has been changed.
        #
        # Example: An external DOI (i.e. DOI not managed by us) can be changed
        # on a published record. Changes are handled by removing the old PID
        # and adding the new.
        changed_pids = {}
        for scheme in draft_schemes.intersection(record_schemes):
            record_id = record_pids[scheme]["identifier"]
            draft_id = draft_pids[scheme]["identifier"]
            if record_id != draft_id:
                changed_pids[scheme] = record_pids[scheme]

        self.service.pids.pid_manager.discard_all(changed_pids)

        # Determine schemes which are required, but not yet created.
        missing_required_schemes = required_schemes - record_schemes - draft_schemes
        # Create all PIDs specified on draft and all missing required PIDs
        pids = self.service.pids.pid_manager.create_all(
            draft,
            pids=draft_pids,
            schemes=missing_required_schemes,
        )

        # Reserve all created PIDs and store them on the record
        self.service.pids.pid_manager.reserve_all(draft, pids)
        record.pids = pids

        # Async register/update tasks after transaction commit.
        for scheme in pids.keys():
            self.uow.register(TaskOp(register_or_update_pid, record["id"], scheme))
