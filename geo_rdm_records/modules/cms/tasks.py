# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records tasks."""

import requests
from celery import shared_task


#
# Tasks
#
@shared_task
def create_feed_post(feed_api, feed_token, feed_post):
    """Create a Feed Post in the GEO Knowledge Hub CMS."""
    res = requests.post(
        url=feed_api,
        headers={
            "Authorization": f"Bearer {feed_token}",
            "Content-Type": "application/json",
        },
        json=dict(data=feed_post),
    )

    res.raise_for_status()
