#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from ckan.tests import factories, helpers


class DataFactory(object):
    '''
    A helper class for creating and manipulating standard test datasets.
    '''

    def __init__(self):
        self.sysadmin = None
        self.org = None
        self.public_records = None
        self.public_no_records = None
        self.private_records = None
        self.author = None
        self.title = None
        self.refresh()

    def _package_data(self, is_private=False):
        '''
        Returns a dictionary with some standard package metadata, with an
        optional 'private' flag.
        :param is_private: Whether the package should be private or not.
        :return: dict
        '''
        return {
            u'notes': u'these are some notes',
            u'dataset_category': u'cat1',
            u'author': self.author,
            u'title': self.title,
            u'private': is_private,
            u'owner_org': self.org[u'id']
            }

    def _resource_data(self, pkg_id, records=None):
        '''
        Returns a dictionary with some standard dictionary, including an
        associated package ID. Records are optional.
        :param pkg_id: The ID of the package to associate the resource to.
        :param records: Optionally, a list of records.
        :return: dict
        '''
        resource = factories.Resource()
        data = {
            u'resource': {
                u'id': resource[u'id'],
                u'package_id': pkg_id,
                u'name': u'Test records',
                u'owner_org': self.org[u'id']
                },
            u'fields': [{
                u'id': u'common_name',
                u'type': u'text'
                }, {
                u'id': u'scientific_name',
                u'type': u'text'
                }]
            }
        if records:
            data[u'records'] = records
        return data

    @property
    def _records(self):
        '''
        A standard list of example records.
        :return: list
        '''
        return [{
            u'common_name': u'Egyptian vulture',
            u'scientific_name': u'Neophron percnopterus'
            }, {
            u'common_name': u'Malabar squirrel',
            u'scientific_name': u'Ratufa indica'
            }, {
            u'common_name': u'Screamer, crested',
            u'scientific_name': u'Chauna torquata'
            }, {
            u'common_name': u'Heron, giant',
            u'scientific_name': u'Ardea golieth'
            }, {
            u'common_name': u'Water monitor',
            u'scientific_name': u'Varanus salvator'
            }]

    def long_title(self):
        '''
        Set the title to a long string, so any new packages that are created
        use the long title.
        '''
        self.title = u"This is a very long package title that's going " \
                     u'to make the tweet exceed 140 characters, ' \
                     u'which would be a shame.'

    def long_author(self):
        '''
        Set the author to a long semicolon-delimited string, so any new
        packages use this long author string.
        '''
        self.author = u'Waylon Dalton; Justine Henderson; ' \
                      u'Abdullah Lang; Marcus Cruz; Thalia Cobb; ' \
                      u'Mathias Little; Eddie Randolph; ' \
                      u'Angela Walker; Lia Shelton; Hadassah Hartman; ' \
                      u'Joanna Shaffer; Jonathon Sheppard'

    def deactivate_package(self, pkg_id):
        '''
        Sets a package's state to 'inactive'. Reloads all the internal package
        dictionaries afterwards so they are up-to-date.
        :param pkg_id: The package to deactivate.
        '''
        pkg_dict = toolkit.get_action(u'package_show')(self.context, {
            u'id': pkg_id
            })
        pkg_dict[u'state'] = u'inactive'
        toolkit.get_action(u'package_update')(self.context, pkg_dict)
        self.reload_pkg_dicts()

    def activate_package(self, pkg_id):
        '''
        Sets a package's state to 'active'. Reloads all the internal package
        dictionaries afterwards so they are up-to-date.
        :param pkg_id: The package to activate.
        '''
        pkg_dict = toolkit.get_action(u'package_show')(self.context, {
            u'id': pkg_id
            })
        pkg_dict[u'state'] = u'active'
        toolkit.get_action(u'package_update')(self.context, pkg_dict)
        self.reload_pkg_dicts()

    def remove_public_resources(self):
        '''
        Delete all resources from the public_records package defined in this
        class. Reloads all the internal package dictionaries afterwards so
        they are up-to-date.
        '''
        for r in self.public_records[u'resources']:
            toolkit.get_action(u'resource_delete')(self.context, {
                u'id': r[u'id']
                })
        self.reload_pkg_dicts()

    def deactivate_public_resources(self):
        '''
        Does not make any actual database changes - makes a copy of the
        current public_records package dictionary and mocks deactivating all
        its resources by setting their states to 'draft'. Returns this mock
        dictionary.
        :return: dict
        '''
        pkg_dict = self.public_records.copy()
        resources_dict = pkg_dict[u'resources']
        for r in resources_dict:
            r[u'state'] = u'draft'
        pkg_dict[u'resources'] = resources_dict
        return pkg_dict

    def _make_resource(self, pkg_id, records=None):
        '''
        Creates a resource in the datastore.
        :param pkg_id: The package ID to associate the resource with.
        :param records: Records to add to the resource, if any.
        '''
        data = self._resource_data(pkg_id, records)
        toolkit.get_action(u'datastore_create')(self.context, data)

    def create(self):
        '''
        Runs all the creation functions in the class, e.g. creating a test
        org and test datasets.
        '''
        self.sysadmin = factories.Sysadmin()
        self.org = factories.Organization()
        self.public_records = factories.Dataset(**self._package_data())
        self._make_resource(self.public_records[u'id'], self._records)

        self.public_no_records = factories.Dataset(**self._package_data())
        self._make_resource(self.public_no_records[u'id'])

        self.private_records = \
            factories.Dataset(**self._package_data(True))
        self._make_resource(self.private_records[u'id'], self._records)

        self.reload_pkg_dicts()

    def destroy(self):
        '''
        Resets the database and any class variables that have been altered,
        e.g. title string.
        '''
        helpers.reset_db()
        self.author = u'Test Author'
        self.title = u'A test package'

    def refresh(self):
        '''
        Resets and recreates the data. Mostly for convenience.
        '''
        self.destroy()
        self.create()

    @property
    def context(self):
        '''
        Defines a context to operate in, using the sysadmin user. Defined as
        a property to work around an authentication issue in ckanext-harvest.
        :return: dict
        '''
        context = {
            u'user': self.sysadmin[u'name'],
            u'ignore_auth': True
            }
        # to fix an issue in ckanext-harvest (commit f315f41)
        context.pop(u'__auth_audit', None)
        return context

    def reload_pkg_dicts(self):
        '''
        Refreshes the package information from the database for each of the
        class' defined packages.
        '''
        self.public_records = toolkit.get_action(u'package_show')(self.context, {
            u'id': self.public_records[u'id']
            })
        self.public_no_records = toolkit.get_action(u'package_show')(self.context, {
            u'id': self.public_no_records[u'id']
            })
        self.private_records = toolkit.get_action(u'package_show')(self.context, {
            u'id': self.private_records[u'id']
            })


class Configurer(object):
    '''
    A class for easily and consistently accessing, resetting, and otherwise
    manipulating the current pylons config within tests.
    '''

    def __init__(self, debug=True):
        self.debug = debug
        self.stored = None
        self._changed = {}
        self.store()
        self.reset()

    def store(self):
        '''
        Stores a copy of the current pylons config.
        '''
        self.stored = toolkit.config.copy()

    @property
    def current(self):
        '''
        Returns the current pylons config.
        :return: PylonsConfig
        '''
        return toolkit.config

    def reset(self):
        '''
        Overwrites the current pylons config with the stored config,
        then sets the debug value to ensure that this is consistent.
        '''
        toolkit.config.update(self.stored)
        self.update({
            u'ckanext.twitter.debug': self.debug
            })

    def update(self, new_values):
        '''
        Updates the config with the specified values and stores the old
        value of each in case it needs to be reverted to.
        :param new_values: A dictionary of config keys and new values.
        '''
        for key, value in new_values.items():
            if key not in self._changed.keys():
                self._changed[key] = toolkit.config.get(key, None)
            toolkit.config[key] = value

    def remove(self, keys):
        '''
        Removes a list of keys from the config, but stores their old values
        first in case they need to be restored.
        :param keys: A list of keys to be removed from the config.
        '''
        for k in keys:
            if k not in self._changed.keys():
                self._changed[k] = toolkit.config.get(k, None)
            if k in toolkit.config.keys():
                del toolkit.config[k]

    def undo(self, key):
        '''
        Restore the old value of a single key. If it wasn't in the config to
        start with or it was never changed, it is deleted.
        :param key: The key to revert.
        '''
        if key in self._changed.keys() and self._changed.get(key, None):
            toolkit.config[key] = self._changed[key]
        else:
            del toolkit.config[key]
        del self._changed[key]
