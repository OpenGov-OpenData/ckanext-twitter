#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from ckan.common import session
from ckan.plugins import toolkit
from ckanext.twitter.lib import (parsers as twitter_parsers)


class TwitterJSHelpers(object):
    '''
    A class defining various methods to pass into the templates as helpers.
    '''

    @property
    def context(self):
        '''
        Convenience wrapper to retrieve the current context as a dictionary.
        :return: dict
        '''
        try:
            c = toolkit.c.__dict__
        except AttributeError:
            c = dict(toolkit.c)
        return c

    def _get_package(self, package_name_or_id):
        '''
        Gets the package dictionary.
        :param package_name_or_id: Preferably the package ID, but either the
        name or ID.
        :return: dict
        '''
        return toolkit.get_action(u'package_show')(self.context, {
            u'id': package_name_or_id
            })

    def _is_new(self, package_id):
        '''
        Tests to see if the package is "new", i.e. it has only just had its
        first resource added.
        :param package_id: The ID of the package to check.
        :return: boolean
        '''
        revisions = toolkit.get_action(u'package_activity_list')(self.context, {
            u'id': package_id
            })
        return len(revisions) <= 3

    def tweet_ready(self, package_id):
        '''
        Checks the session to see if the package has been marked as ready
        for tweeting via the update hook. Removes the 'twitter_is_suitable'
        key from the session if present.
        :param package_id: The package ID.
        :return: boolean
        '''
        in_session = session.pop(u'twitter_is_suitable', u'') == package_id
        return in_session

    def get_tweet(self, package_id):
        '''
        Generates the tweet text for the given package.
        :param package_id: The package ID.
        :return: str
        '''
        return twitter_parsers.generate_tweet(self.context, package_id,
                                              self._is_new(package_id))


def twitter_pkg_suitable(context, pkg_id, pkg_dict=None):
    '''
    Various tests to determine if a package is suitable for tweeting about,
    e.g. it's active & has resources.
    :param context: The current context.
    :param pkg_id: The package ID.
    :param pkg_dict: Optionally provided instead of pkg_id to avoid
    requesting from the API. Not recommended - provided as a test helper.
    :return: boolean
    '''
    if pkg_dict:
        package = pkg_dict
    else:
        try:
            package = toolkit.get_action(u'package_show')(context, {
                u'id': pkg_id
                })
        except toolkit.ObjectNotFound:
            return False
    if package.get(u'state', u'') != u'active' and package.get(u'state',
                                                               u'') != u'draft':
        return False
    resources = package.get(u'resources', [])
    if len(resources) == 0:
        return False
    if not any([r.get(u'state', u'') == u'active' for r in resources]):
        return False
    if package.get(u'private', False):
        return False
    return True
