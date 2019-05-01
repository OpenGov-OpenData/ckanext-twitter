#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from datetime import datetime as dt

from beaker.cache import Cache

from ckanext.twitter.lib import config_helpers

twitter_cache = Cache(u'twitter')


def cache(pkg_id):
    '''
    Adds the package id and current time to the 'twitter' cache. Clears any
    existing entries for the given package id first.
    :param pkg_id: The package id to store.
    '''
    twitter_cache.remove_value(pkg_id)
    twitter_cache.put(pkg_id, dt.now())


def reset_cache():
    '''
    Clears everything from the 'twitter' cache.
    '''
    twitter_cache.clear()


def remove_from_cache(pkg_id):
    '''
    Remove the package id from the cache.
    :param pkg_id:
    '''
    twitter_cache.remove_value(pkg_id)


def expired(pkg_id):
    '''
    Checks to see if the cache entry for the package's last tweet (if any)
    is old enough to be overwritten.
    :param pkg_id: The package ID.
    :return: boolean
    '''
    if not twitter_cache.has_key(pkg_id):
        return True
    last_posted = twitter_cache.get(pkg_id)
    hours_since = ((dt.now() - last_posted).seconds / 3600)
    return hours_since > config_helpers.twitter_hours_between_tweets()
