#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

import ckan.lib.base as base
from ckan.common import c
from ckanext.twitter.lib import twitter_api


class TweetController(base.BaseController):
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
        body = dict(c.pylons.request.postvars)
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
