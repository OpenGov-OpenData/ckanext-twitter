#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import math

import re
from jinja2 import Environment

from ckan.plugins import toolkit
from ckanext.twitter.lib import config_helpers

tweet_limit = 140


def extract_info(context, pkg_dict, template_length, tokens):
    '''
    Creates a simplified dictionary for use in a tweet string template.
    :param context: The current context.
    :param pkg_dict: The package information to be simplified.
    :param template_length: The length of the text in the template (without
    any of the tokens).
    :param tokens: A list of token names in the template (extracted via regex).
    :return: dict
    '''
    # get the values that are simple (i.e. not lists or dicts)
    simplified = {k: v for k, v in pkg_dict.items() if
                  not isinstance(v, list) and not isinstance(v,
                                                             dict) and v is
                  not None}

    # turn the lists into counts
    list_lengths = {k: len(v) for k, v in pkg_dict.items() if
                    isinstance(v, list) or isinstance(v, dict)}
    for k, v in list_lengths.items():
        simplified[k] = v

    # apply specific rules to certain fields
    simplified[u'records'] = get_number_records(context, pkg_dict[u'id'])
    simplified[u'author'] = truncate_author(simplified.get(u'author', u'Anon.'))

    # truncate other fields
    other_tokens = [t for t in tokens if
                    t not in [u'records', u'author'] and t in simplified.keys()]
    max_total_token = tweet_limit - template_length
    total_token = sum([len(str(simplified[t])) for t in tokens if
                       t in [u'records', u'author']])
    for i in range(len(other_tokens)):
        char_limit = math.floor(
            (max_total_token - total_token) / (len(other_tokens) - i))
        val = unicode(simplified.get(other_tokens[i], u'')).strip()
        if len(val) > char_limit:
            val = truncate_field(val, char_limit)
        simplified[other_tokens[i]] = val
        total_token += len(val)
    return simplified


def truncate_author(author):
    '''
    Shortens the author field using regular expressions.
    :param author: The full author string.
    :return: str
    '''
    sep_rgx = u'\s?[,;]\s?'
    name_sep_rgx = u'(?<=[^,;])\s'
    separators = list(set(re.findall(sep_rgx, author)))
    name_sep = re.search(name_sep_rgx, author)
    if len(separators) == 0:
        return re.split(name_sep_rgx, author)[-1] if name_sep else author
    first_author = re.split(sep_rgx, author)[0]
    if len(separators) == 1:
        first_author = re.split(name_sep_rgx, first_author)[1]
    return u'{0} et al.'.format(first_author)


def truncate_field(value, char_limit):
    '''
    Shortens the given value to a length equal to or less than the character
    limit and appends a continuation marker.
    :param value: The value to be truncated.
    :param char_limit: The maximum number of characters in the output string.
    :return: str
    '''
    marker = u'[...]'
    truncated = []
    if u' ' in value:
        parts = value.split(u' ')
        for p in parts:
            if sum([len(i) + 1 for i in truncated]) + len(p) + len(
                    marker) < char_limit:
                truncated.append(p)
            else:
                break
        return u' '.join(truncated) + marker
    return value[:char_limit - len(marker)] + marker


def get_number_records(context, pkg_id):
    '''
    Counts the total number of records associated with a package.
    :param context: The current context.
    :param pkg_id: The package ID.
    :return: int
    '''
    pkg = toolkit.get_action(u'package_show')(context, {
        u'id': pkg_id
        })
    resources = pkg.get(u'resources', None)
    if not resources or len(resources) == 0:
        return 0
    resource_ids = [r[u'id'] for r in resources]
    total = 0
    for rid in resource_ids:
        try:
            resource_data = toolkit.get_action(u'datastore_search')(context, {
                u'resource_id': rid
                })
            total += resource_data.get(u'total', 0)
        except toolkit.ObjectNotFound:
            pass
    return total


def generate_tweet(context, pkg_id, is_new, force_truncate=True):
    '''
    Generates a standard tweet based on template values in the pylons
    config. Does not post the tweet; just generates and returns the text.
    :param context: The current context.
    :param pkg_id: The ID of the package to tweet about.
    :param is_new: True if the package has only just been created or given
    its first resource, False if it's being updated.
    :param force_truncate: If True, enforces an extra check at the end to
    ensure the text is below 140 characters. This should not be necessary as
    other methods account for this, but this is an optional final check.
    :return: str
    '''
    pkg = toolkit.get_action(u'package_show')(context, {
        u'id': pkg_id
        })
    if pkg.get(u'private', False):
        return
    format_string = config_helpers.twitter_new_format() \
        if is_new else \
        config_helpers.twitter_updated_format()
    tokens = re.findall(u'(?:{{ )(\w+)(?:(?:|.+?)? }})', format_string)
    template = Environment().from_string(format_string)
    simplified_dict = extract_info(context, pkg,
                                   len(unicode(template.module)), tokens)
    rendered = template.render(simplified_dict)
    # extra check to make sure the tweet isn't too long
    if len(rendered) > tweet_limit and force_truncate:
        rendered = rendered[:tweet_limit]
    return rendered
