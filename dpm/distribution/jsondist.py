import os
try:
    import json
except ImportError:
    import simplejson as json

from dpm.package import Package
from base import DistributionBase

class JsonDistribution(DistributionBase):
    '''Simple distribution storing metadata in json files.

        {dist-path}/datapackage.json
    
          * package metadata in json format.

        {dist-path}/data/....

            # Data files
    '''
    metadata_filename = 'datapackage.json'

    @classmethod
    def load(self, path):
        '''Load a L{Package} object from a path to a package distribution.
        
        @return: the Distribution object.
        '''
        pkg = Package()
        pkg.installed_path = path 
        metadata_path = os.path.join(path, self.metadata_filename)
        fo = open(metadata_path)
        metadata = json.load(fo)
        readme_notes = self._get_notes_from_readme(path)
        if readme_notes:
            metadata['notes'] = readme_notes
        pkg.update_metadata(metadata)
        fo.close()
        return self(pkg)
    
    @classmethod
    def _get_notes_from_readme(cls, path):
        files = [ fn for fn in os.listdir(path) if
                fn.lower().startswith('readme') ]
        preferred = [ fn for fn in os.listdir(path) if 
                fn.lower().startswith('readme.dpm') ]
        if preferred:
            # make sure it gets used first
            files.insert(0, preferred[0])
        if files:
            fo = open(os.path.join(path, files[0]))
            out = fo.read().decode('utf8', 'replace')
            fo.close()
            return out
        else:
            return ''

    def write(self, path, **kwargs):
        '''Write this distribution to disk at `path`.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        # write README
        notes = self.package.metadata.get('notes', '')
        readme_fp = os.path.join(path, 'README.dpm.markdown')
        fo = open(readme_fp, 'w')
        fo.write(notes.encode('utf8'))
        fo.close()
        # write metadata
        if 'notes' in self.package.metadata:
            del self.package.metadata['notes']
        metadata_path = os.path.join(path, self.metadata_filename)
        fo = open(metadata_path, 'w')
        json.dump(self.package.metadata, fo, indent=2, sort_keys=True)
        fo.close()
        # create empty 'data' directory
        datadir = os.path.join(path, 'data')
        if not os.path.exists(datadir):
            os.makedirs(datadir)
