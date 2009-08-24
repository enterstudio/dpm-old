import datapkg.metadata as M
import distutils.dist

class TestMetadataConverter:
    def test_1(self):
        inmeta = distutils.dist.DistributionMetadata()
        inmeta.name = 'XXX'
        inmeta.description = 'xyz'
        inmeta.long_description = '''A whole bunch of stuff ...'''
        outmeta = M.MetadataConverter.from_distutils(inmeta)
        assert outmeta['title'] == 'xyz', outmeta
        assert outmeta['name'] == 'XXX'
        assert outmeta['notes'] == inmeta.long_description, outmeta

    def test_with_summary(self):
        inmeta = distutils.dist.DistributionMetadata()
        inmeta.name = 'XXX'
        inmeta.summary = 'YYY'
        inmeta.description = 'xyz'
        outmeta = M.MetadataConverter.from_distutils(inmeta)
        assert outmeta['name'] == 'XXX'
        assert outmeta['title'] == 'YYY'
        assert outmeta['notes'].endswith(inmeta.description), outmeta
