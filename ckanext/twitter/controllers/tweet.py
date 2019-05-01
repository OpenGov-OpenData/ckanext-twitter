#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

from ckan.plugins import toolkit
from ckanext.twitter.lib import twitter_api, cache_helpers


class TweetController(toolkit.BaseController):
    '''
    A class exposing tweet functions as AJAX endpoints.
    '''

    def send(self, pkg_id):
        '''
        Posts the tweet given in the request body. The package ID is
        required for caching. Returns json data for displaying success/error
        messages.
        :param pkg_id: The package ID (for caching).
        :return: str
        '''
        body = dict(toolkit.request.postvars)
        text = body.get(u'tweet_text', None)
        if text:
            posted, reason = twitter_api.post_tweet(text, pkg_id)
        else:
            posted = False
            reason = u'no tweet defined'
        return json.dumps({
            u'success': posted,
            u'reason': reason,
            u'tweet': text if text else u'tweet not defined'
            })

    def clear(self, pkg_id):
        cache_helpers.remove_from_cache(pkg_id)
        if u'twitter_is_suitable' in session:
            del session[u'twitter_is_suitable']
            session.save()
