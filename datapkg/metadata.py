import os

class Metadata(dict):
    key_list = [
       'name', 
       'title',
       'version',
       'license',
       'author',
       'maintainer',
       'url',
       'download_url',
       'notes',
       'tags',
       'extras',
       ]
    defaults = { 'tags': [], 'extras': {} }


class MetadataConverter(object):
    @classmethod
    def from_distutils(self, data):
        '''Convert distutils metadata to a simple metadata dictionary suitable
        for our consumption.

        @param data: a `distutils.dist.DistributionMetadata` instance
        '''
        # bit of a nightmare here since we can load either direct from setup.py
        # or from PKG-INFO
        # In PKG-INFO description in the setup.py becomes a summary and
        # long_description becomes description ...
        # Note also keywords are comma separated!
        inmeta = {}
        # python distutils/PKG-INFO attr names
        attrnames = set(data._METHOD_BASENAMES)
        attrnames.remove('fullname')
        attrnames.remove('contact_email')
        attrnames.remove('contact')
        attrnames.add('summary')
        for attrname in attrnames:
            value = getattr(data, attrname, None) or ''
            inmeta[attrname] = unicode(value, encoding='utf8', errors='ignore') 
        distutils_keymap = {
            'summary': 'title',
            'description': 'title',
            'long_description': 'notes',
            'keywords': 'tags',
            }
        # in case where loading from PKG-INFO
        if inmeta['summary']:
            distutils_keymap['description'] = 'notes'
        else:
            del distutils_keymap['summary']
        newmeta = self.normalize_metadata(inmeta, distutils_keymap)
        return newmeta

    @classmethod
    def to_distutils(self, metadata):
        distutils_metadata = distutils.dist.DistributionMetadata()
        for key, value in metadata.items():
            # TODO: use the keymap ...
            # TODO: tags may be list not a string ...
            setkey = key
            tval = value
            if key == 'tags':
                setkey = 'keywords'
            elif key == 'title':
                setkey = 'description'
            elif key == 'notes':
                setkey = 'long_description'
            setattr(distutils_metadata, setkey, tval)
        return distutils_metadata

    @classmethod
    def normalize_metadata(self, metadata, keymap=None):
        if keymap is None:
            keymap = {}
        newmeta = dict(metadata)
        extras = {}
        if not 'name' in newmeta and 'id' in newmeta:
            newmeta['name'] = newmeta['id']
        if not 'extras' in newmeta:
            newmeta['extras'] = {}
        for inkey,value in metadata.items():
            if inkey in Metadata.key_list:
                continue
            elif inkey in keymap:
                actualkey = keymap[inkey]
                # special case where we append to existing values (as e.g. we
                # may be running together description and comments)
                if actualkey == 'notes':
                    # TODO: do we need to trim leading '\n' that may result?
                    newmeta[actualkey] = newmeta.get(actualkey, '') + os.linesep + value
                elif not actualkey in newmeta:
                    newmeta[actualkey] = value
            else:
                newmeta['extras'][inkey] = value
        if 'notes' in newmeta and newmeta['notes'].startswith(os.linesep):
            newmeta['notes'] = newmeta['notes'][len(os.linesep):]
        # TODO: normalize tags (?) (space separated list)
        return newmeta

