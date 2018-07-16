import ckan.plugins as p
import ckanext.twitter.lib.config_helpers
from ckan.plugins import toolkit as tk
from beaker.cache import cache_regions
from ckan.common import session
from ckanext.twitter.lib import config_helpers, helpers as twitter_helpers
class TwitterPlugin(p.SingletonPlugin):
    '''
    Automatically send tweets when a dataset is updated or created.
    '''
    p.implements(p.IConfigurable, inherit = True)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers, inherit = True)
    p.implements(p.IRoutes, inherit = True)
    p.implements(p.IResourceController, inherit = True)
    
    # IConfigurable
    def configure(self, config):
        cache_regions.update({
            'twitter': {
                'expire':
                    ckanext.twitter.lib.config_helpers
                        .twitter_hours_between_tweets(),
                'type': 'memory',
                'enabled': True,
                'key_length': 250
                }
            })

    # IConfigurer
    def update_config(self, config):
        # Add templates
        p.toolkit.add_template_directory(config, 'theme/templates')
        # Add resources
        p.toolkit.add_resource('theme/fanstatic', 'ckanext-twitter')


    # IResourceController, called after a resource is created
    def after_create(self, context, resource):
        data_dict = {'id': resource['package_id']}
        pkg_dict = tk.get_action('package_show')(context, data_dict)

        is_suitable = twitter_helpers.twitter_pkg_suitable(context,
                                                           pkg_dict['id'])
        if is_suitable and ('Twitter_Popup' in pkg_dict.get('twitter_popup', [])):
            try:
                session.pop('twitter_is_suitable', '')
                session.setdefault('twitter_is_suitable', pkg_dict['id'])
                session.save()
            except TypeError:
                print "session not iterable"


    # IResourceController, called after a resource is updated
    def after_update(self, context, resource):
        data_dict = {'id': resource['package_id']}
        pkg_dict = tk.get_action('package_show')(context, data_dict)

        is_suitable = twitter_helpers.twitter_pkg_suitable(context,
                                                           pkg_dict['id'])
        if is_suitable and ('Twitter_Popup' in pkg_dict.get('twitter_popup', [])):
            try:
                session.pop('twitter_is_suitable', '')
                session.setdefault('twitter_is_suitable', pkg_dict['id'])
                session.save()
            except TypeError:
                print "session not iterable"

    # ITemplateHelpers
    def get_helpers(self):
        js_helpers = twitter_helpers.TwitterJSHelpers()
        return {
            'tweet_ready': js_helpers.tweet_ready,
            'get_tweet': js_helpers.get_tweet,
            'disable_edit': config_helpers.twitter_disable_edit
            }

    # IRoutes
    def before_map(self, _map):
        controller = 'ckanext.twitter.controllers.tweet:TweetController'
        _map.connect('post_tweet', '/dataset/{pkg_id}/tweet',
                     controller = controller, action = 'send',
                     conditions = {
                         'method': ['POST']
                         })
        _map.connect('no_tweet', '/dataset/disable-tweet-popup',
                     controller = controller, action = 'disable_tweet_popup',
                     conditions = {
                         'method': ['POST']
                         })
        return _map
