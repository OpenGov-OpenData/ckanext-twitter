# ckanext-twitter

Note this README is unique to CHHS!

Sends a tweet every time a dataset with the twitter popup field enabled is created or a resource within that dataset is added or updated.


# Requirements

This CHHS specific version of the Twitter Extension requires [ckanext-chhs_schema](https://github.com/OpenGov-OpenData/ckanext-chhs_schema).

# Setup

1. Clone the repository into the virtual env's `src` folder:

  ```bash
  cd /usr/lib/ckan/default/src/
  git clone https://github.com/NaturalHistoryMuseum/ckanext-twitter.git
  ```

2. Activate the virtual env:

  ```bash
  . /usr/lib/ckan/default/bin/activate
  ```

3. Run setup.py:

  ```bash
  cd /usr/lib/ckan/default/src/ckanext-twitter
  python setup.py develop
  ```

4. Add 'twitter' to the list of plugins in your config file:

  ```ini
  ckan.plugins = ... twitter
  ```

5. Install the requirements from requirements.txt:

  ```bash
  cd /usr/lib/ckan/default/src/ckanext-twitter
  pip install -r requirements.txt
  ```

# Configuration

There are a number of options that can be specified in your .ini config file. The only _required_ options are the twitter credentials. Everything else has a sensible default set.

## Twitter Credentials **[REQUIRED]**
Place these configurations in your revelant .ini file below your plugin settings.

```ini
ckanext.twitter.consumer_key = YOUR-CONSUMER-KEY
ckanext.twitter.consumer_secret = YOUR-CONSUMER-SECRET
ckanext.twitter.token_key = YOUR-TOKEN-KEY
ckanext.twitter.token_secret = YOUR-TOKEN-SECRET
```

All of these can be obtained by creating a single-user app at [apps.twitter.com](https://apps.twitter.com). They can be found on the "keys and access tokens" tab when viewing your app.

## Tweet Templates

Tweets are generated using Jinja2 and a set of parsers to extract/shorten common pieces of information from the package dictionary. These templates can be overwritten in the config.

The default for `ckanext.twitter.new` (the option for the 'new dataset' tweet template) is:
```html+jinja
New dataset: "{{ title }}" by {{ author }} ({%- if records != 0 -%} {{ records }} records {%- else -%} {{ resources }} resource {%- endif -%}).
```

And the default for `ckanext.twitter.updated` is:
```html+jinja
Updated dataset: "{{ title }}" by {{ author }} ({%- if records != 0 -%} {{ records }} records {%- else -%} {{ resources }} resource {%- endif -%}).
```

If your config is created dynamically using Jinja2, you will have to wrap any custom template in `{% raw %}{% endraw %}` tags and add a newline after it, e.g.:
```ini
ckanext.twitter.new = {% raw %}{{ title }} by {{ author }} ({{ records }} records) has just been published!{% endraw %}

ckanext.twitter.consumer_key = {{ twitter.consumer_key }}
ckanext.twitter.consumer_secret = {{ twitter.consumer_secret }}
ckanext.twitter.token_key = {{ twitter.token_key }}
ckanext.twitter.token_secret = {{ twitter.token_secret }}
```

Token values will come from a simplified package dictionary where any collection values (i.e. lists and dictionaries) have been replaced with the number of items, the author list has been significantly shortened, and any long strings will be shortened to fit into the tweet character limit (currently set at 140).
Some example keys:
```
owner_org
private
num_tags
id
metadata_created
metadata_modified
author
type
num_resources
records
name
isopen
notes
title
organization
```

## Other options

Name|Description|Default
--|---|--
`ckanext.twitter.debug`|Is in debug mode; overrides global debug flag if specified|False
`ckanext.twitter.hours_between_tweets`|Number of hours between tweets about the _same dataset_ (to prevent spamming)|24  
`ckanext.twitter.disable_edit`|If true, users will not be able to edit the tweet about their dataset before it is posted (though they can still decide not to post it)|False

# Testing

_None of the tests should actually post any tweets to Twitter._

They will test authentication, but _nothing should be posted_.

To run the tests, use nosetests inside your virtualenv. The `--nocapture` flag will allow you to see the tweets being printed to the console instead of posted to twitter (as the tests are mostly run in debug mode) but will also print a lot of statements about database manipulation.
```bash
nosetests --ckan --with-pylons=/path/to/your/test.ini --where=/path/to/your/install/directory/ckanext-twitter --nologcapture --nocapture
```
