import pylons


def twitter_get_credentials():
    '''
    Retrieves twitter API key and secret from config file.
    :return: (key, secret)
    '''
    consumer_key = pylons.config.get('ckanext.twitter.consumer_key',
                                     'no-consumer-key-set')
    consumer_secret = pylons.config.get('ckanext.twitter.consumer_secret',
                                        'no-consumer-secret-set')
    token_key = pylons.config.get('ckanext.twitter.token_key',
                                  'no-token-key-set')
    token_secret = pylons.config.get('ckanext.twitter.token_secret',
                                     'no-token-secret-set')
    return consumer_key, consumer_secret, token_key, token_secret


def twitter_is_debug():
    '''
    Checks debug flags in the config - the plugin-specific flag can override
    the global debug flag.
    :return: boolean
    '''
    return pylons.config.get('ckanext.twitter.debug',
                             pylons.config.get('debug', False))


def twitter_hours_between_tweets():
    '''
    For calculating the 'rest period' between subsequent tweets about the
    same dataset.
    :return: int
    '''
    return pylons.config.get('ckanext.twitter.hours_between_tweets', 24)



def twitter_new_format():
    '''
    Gets the string defining the format of the tweet that will be posted for
    new datasets.
    :return: string with replaceable jinja2 tags
    '''
    return pylons.config.get('ckanext.twitter.new',
                             'New dataset: "{{ title }}" by {{ author }} ({'
                             '%- if records != 0 -%} {{ records }} records {'
                             '%- else -%} {{ resources }} resource {%- endif '
                             '-%}).')


def twitter_updated_format():
    '''
    Gets the string defining the format of the tweet that will be posted for
    updated.
    :return: string with replaceable jinja2 tags
    '''
    return pylons.config.get('ckanext.twitter.updated',
                             'Updated dataset: "{{ title }}" by {{ author }} '
                             '({%- if records != 0 -%} {{ records }} records '
                             '{%- elif resources == 1 -%} {{ resources }} '
                             'resource {%- else -%} {{ resources }} '
                             'resources {%- endif -%}).')


def twitter_disable_edit():
    '''
    Checks for a disable_edit flag in the config. If true, this prevents the
    user editing the tweet before it is posted.
    :return: boolean
    '''
    return pylons.config.get('ckanext.twitter.disable_edit', False)
