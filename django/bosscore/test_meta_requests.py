from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from django.http import HttpRequest
from rest_framework.request import Request

from .request import BossRequest
from .views import BossMeta
from .models import *

from django.conf import settings
version  = settings.BOSS_VERSION

class BossCoreMetaRequestTests(APITestCase):
    """
    Class to test Meta data requests
    """

    def setUp(self):
        """
        Initialize the test database with some objects
        :return:
        """
        self.rf = APIRequestFactory()

        col = Collection.objects.create(name='col1')
        exp = Experiment.objects.create(name='exp1', collection=col)
        cf = CoordinateFrame.objects.create(name='cf1', x_extent=1000, y_extent=10000, z_extent=10000,
                                                    x_voxelsize=4, y_voxelsize=4, z_voxelsize=4)
        ds = Dataset.objects.create(name='ds1', experiment=exp, coord_frame=cf)
        channel = Channel.objects.create(name='channel1', dataset=ds)
        ts = TimeSample.objects.create(name='ts1', channel=channel)
        layer = Layer.objects.create(name='layer1', time=ts)
        ds.default_channel = channel
        ds.default_time = ts
        ds.default_layer = layer
        ds.save()

        ds = Dataset.objects.create(name='ds5', experiment=exp, coord_frame=cf)
        channel = Channel.objects.create(name='channel5', dataset=ds)
        ts = TimeSample.objects.create(name='ts5', channel=channel)
        layer = Layer.objects.create(name='layer5', time=ts)

    def test_bossrequest_meta_init_valid_collection(self):
        """
        Test initialization of requests from the meta data service with collection
        :return:
        """
        # create the request with collection name
        url = '/' + version + '/meta/col1/?key=mkey'
        expectedValue = 'col1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version

        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_collection(), expectedValue)

    def test_bossrequest_meta_init_not_found(self):
        """
        Test initialization of requests from the meta data service names of objects not in the database
        :return:
        """
        # create the request with collection name
        url = '/' + version + '/meta/col2/?key=mkey'
        expectedValue = None
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        #ret = BossRequest(drfrequest)
        #self.assertEqual(ret.get_collection(), expectedValue)

        # Test With experiment not found
        url = '/' + version+ '/meta/col1/exp2/ds1/?key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        #ret = BossRequest(drfrequest)
        #self.assertEqual(ret.get_experiment(), None)

        # Test with dataset not found
        url = '/' + version + 'meta/col1/exp1/ds2/?key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        #ret = BossRequest(drfrequest)
        #self.assertEqual(ret.get_dataset(), None)

    def test_bossrequest_meta_init_valid_col_exp(self):
        """
        Test initialization of requests from the meta data service with a valid collection and experiment
        :return:
        """
        # create the request with collection name and experiment name
        url = '/' + version +'/meta/col1/exp1/?key=mkey'
        expectedCol = 'col1'
        expectedExp = 'exp1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version

        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_collection(), expectedCol)
        self.assertEqual(ret.get_experiment(), expectedExp)

    def test_bossrequest_meta_init_valid_no_optargs(self):
        """
        Test initialization of requests from the meta data service with a valid collection and experiment and dataset but no optional arguments
        :return:
        """
        # create the request with collection name and experiment name
        url = '/' + version + '/meta/col1/exp1/ds1/'
        expectedCol = 'col1'
        expectedExp = 'exp1'
        expectedDs = 'ds1'

        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version

        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_collection(), expectedCol)
        self.assertEqual(ret.get_experiment(), expectedExp)
        self.assertEqual(ret.get_dataset(), expectedDs)

    def test_bossrequest_meta_init_valid_col_exp_ds(self):
        """
        Test initialization of requests from the meta data service with a valid collection and experiment and dataset
        :return:
        """
        # create the request with collection name and experiment name and dataset name
        url = '/' + version + '/meta/col1/exp1/ds1/?key=mkey'
        expectedCol = 'col1'
        expectedExp = 'exp1'
        expectedDs = 'ds1'
        expectedChannel = 'channel1'
        expectedTs = 'ts1'
        expectedLayer = 'layer1'
        expectedCoord = 'cf1'

        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_collection(), expectedCol)
        self.assertEqual(ret.get_experiment(), expectedExp)
        self.assertEqual(ret.get_dataset(), expectedDs)

        # Check coordinate frame
        self.assertEqual(ret.get_coordinate_frame(), expectedCoord)

        # Check default channel, timesample and layer
        self.assertEqual(ret.get_default_channel(), expectedChannel)
        self.assertEqual(ret.get_default_time(), expectedTs)
        self.assertEqual(ret.get_default_layer(), expectedLayer)

    def test_bossrequest_init_optargs_channel(self):
        """
        Test initialization of requests with valid optional arguments (channel)
        :return:
        """
        expectedChannel = 'channel1'

        # create the request with channel name
        url = '/' + version + '/meta/col1/exp1/ds1/channel1/?channel=channel1&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_channel(), expectedChannel)

        # Test with channel name not found

        url = '/' + version +'/meta/col1/exp1/ds1/?channel=channel2&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        #ret = BossRequest(drfrequest)
        #TODO - Test that this throws an error

    def test_bossrequest_init_optargs_channel_timesample(self):
        """
        Test initialization of requests with valid optional args ( channel and timesample)
        :return:
        """
        expectedChannel = 'channel1'
        expectedTs = 'ts1'

        # create the request with channelname and timesamplename
        url = '/' + version +'/meta/col1/exp1/ds1/?channel=channel1&time=ts1&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_channel(), expectedChannel)
        self.assertEqual(ret.get_timesample(), expectedTs)

        # create the request with timesample name not found
        url = '/' + version + '/meta/col1/exp1/ds1/?channel=channel1&time=ts2&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        #ret = BossRequest(drfrequest)
        #TODO - Test that this throws an error

    def test_bossrequest_init_optargs_channel_timesample_layer(self):
        """
        Test initialization of requests with valid option arguments (channel,timesample and layer)
        :return:
        """
        expectedChannel = 'channel1'
        expectedTs = 'ts1'
        expectedLayer = 'layer1'

        # create the request with channel name and timesample name and layer name
        url = '/' + version +'/meta/col1/exp1/ds1/?channel=channel1&time=ts1&layer=layer1&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_channel(), expectedChannel)
        self.assertEqual(ret.get_timesample(), expectedTs)
        self.assertEqual(ret.get_layer(), expectedLayer)

        # create the invalid layer name
        url = '/' + version + '/meta/col1/exp1/ds1/?channel=channel1&time=ts1&layer=layer2&key=mkey'
        request = self.rf.get(url)
        #drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        #response = BossRequest(drfrequest)


    def test_bossrequest_init_optargs_invalid(self):
        """
        Test initialization of requests with invalid/missing option arguments (channel,timesample and layer)
        :return:
        """
        expectedChannel = 'channel5'
        expectedLayer = 'layer5'
        expectedTs = 'ts5'

        # create the request with timesample name and layer name but no channel or default channel
        url = '/' + version + '/meta/col1/exp1/ds5/?timesample=ts5&layer=layer5&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        # TODO ---- Error checking should fix this?
        # ret = BossRequest(drfrequest)
        # self.assertEqual(ret.get_channel(), expectedChannel)

    def test_bossrequest_init_optargs_without_dataset(self):
        """
        Test request with optional arguments but no dataset
        :return:
        """
        # TODO - Think about how to handle this better
        # create the request with out experiment and dataset but with optargs
        url = '/' + version + '/meta/col1/?channel=channel1&key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)

        self.assertEqual(ret.get_channel(), None)
        self.assertEqual(ret.get_timesample(), None)
        self.assertEqual(ret.get_layer(), None)

    def test_get_bosskey_collection(self):
        """
        Test retriving a bossmeta key from  BossRequest object with collection name
        """
        # create the request
        url = '/' +version + '/meta/col1/?key=mkey'
        expectedValue = 'col1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(ret.get_collection(), expectedValue)
        self.assertEqual(bosskey, expectedValue)

        # Invalid collection name
        url = '/'+ version + '/meta/col2/?key=mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        #ret = BossRequest(drfrequest)
        #osskey = ret.get_bosskey()
        #self.assertEqual(ret.get_collection(), None)
        #self.assertEqual(bosskey, None)

    def test_get_bosskey_collection_experiment(self):
        """
        Test retriving a bossmeta key from  BossRequest object with collection name and experimentname
        """
        # create the request
        url = '/' + version + '/meta/col1/exp1/?key=mkey'
        expectedValue = 'col1&exp1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

    def test_get_bosskey_collection_experiment_dataset(self):
        """
        Test retriving a bossmeta key from  BossRequest object with collection name and experimentname and dataset nam
        """
        # create the request
        url = '/' + version + '/meta/col1/exp1/ds1/?key=mkey'
        expectedValue = 'col1&exp1&ds1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

    def test_get_bosskey_optarg(self):
        """ 
        Test bossmeta key with optional arguments
        """

        # only channel
        url = '/' + version +'/meta/col1/exp1/ds1/?channel=channel1&key=mkey'
        expectedValue = 'col1&exp1&ds1&channel1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

        # channel and timesample
        url = '/' + version + '/meta/col1/exp1/ds1/?channel=channel1&time=ts1&key=mkey'
        expectedValue = 'col1&exp1&ds1&channel1&ts1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

        # channel and timesample and layer
        url = '/' + version + '/meta/col1/exp1/ds1/?channel=channel1&time=ts1&layer=layer1&key=mkey'
        expectedValue = 'col1&exp1&ds1&channel1&ts1&layer1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

    def test_get_bosskey_optarg_with_default_channnel(self):
        """
        Test the bossmeta key is generated correctly using the default channel
        """
        # timesample and layer - use default channel
        url = '/' + version + '/meta/col1/exp1/ds1/?timesample=ts1&layer=layer1&key=mkey'
        expectedValue = 'col1&exp1&ds1&channel1&ts1&layer1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

        # layer - use default channel and timesample
        url = '/' + version + '/meta/col1/exp1/ds1/?layer=layer1&key=mkey'
        expectedValue = 'col1&exp1&ds1&channel1&ts1&layer1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

    def test_get_bosskey_optarg_with_default_timesample(self):
        """
        Test the bossmeta key is generated correctly using the default channel
        """
        # timesample and layer - use default channel
        url = '/' + version + '/meta/col1/exp1/ds1/?channel=channel1&layer=layer1&key=mkey'
        expectedValue = 'col1&exp1&ds1&channel1&ts1&layer1'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version

        ret = BossRequest(drfrequest)
        bosskey = ret.get_bosskey()
        self.assertEqual(bosskey, expectedValue)

    def test_get_key(self):
        """
        Test the the get meta key method
        """
        url = '/' + version + '/meta/col1/exp1/ds1/?channel=channel1&layer=layer1&key=mkey'
        expectedValue = 'mkey'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version

        ret = BossRequest(drfrequest)
        key = ret.get_key()
        self.assertEqual(key, expectedValue)

    def test_get_value(self):
        """
        Test the the get meta key method
        """
        url = '/' + version +'/meta/col1/exp1/ds1/?channel=channel1&layer=layer1&key=mkey&value=TestValue'
        expectedValue = 'TestValue'
        request = self.rf.get(url)
        drfrequest = BossMeta().initialize_request(request)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        value = ret.get_value()
        self.assertEqual(value, expectedValue)