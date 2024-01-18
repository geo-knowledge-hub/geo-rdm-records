# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Checker Network management module."""

from datetime import timedelta

import requests
from requests_cache import CachedSession
from retry_requests import retry


def is_link_available(
    url: str,
    requests_config=None,
    retry_config=None,
    cache_config=None,
):
    """Check if a link is available.

    Args:
        url (str): URL to be checked.

        requests_config (dict): ``requests.get`` configurations

        retry_config (dict): ``retry_requests.retry`` configurations

        cache_config (dict): ``requests_cache.CachedSession`` configurations.

    Note:
        By default, the following cases are used to define a link as unavailable:
            - Case 1: Delay to answer longer than 5 seconds;
            - Case 2: No access to the server or a dropped connection;
            - Case 3: An HTTP Answer of 500, 502, or 504.

        To change the value of ``Case 1``, you can use the Request config (``requests_config``). Also,
        to change the value of ``Case 2`` and ``Case 3``, you can use the Retry config (``retry_config``).
    """
    is_available = True

    cache_config = {} if cache_config is None else cache_config
    retry_config = {} if retry_config is None else retry_config
    requests_config = {} if requests_config is None else requests_config

    # building the session object
    session = CachedSession(
        "geo_rdm_records_links_checker",
        cache_control=False,
        expire_after=timedelta(days=30),
        allowable_codes=[200, 400],
        **cache_config
    )

    session = retry(session, **retry_config)

    try:
        session.get(url, **requests_config)
        # nothing to do
    except requests.RequestException as e:
        # If there is any request-related error, the link is not available
        is_available = False

    return is_available
