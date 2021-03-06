# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework.exceptions import Throttled

from django.utils.translation import ugettext_lazy as _
from django.conf import settings as django_settings

import json
import bossutils
import redis
import boto3

def parse_limit(val):
    """Convert a textual representation of a number of bytes into an integer

    NOTE: If val is None then None is returned

    Args:
        val (str): number of bytes
                   Format: <num><unit> where
                           <num> - is a float
                           <unit> is one of K, M, G, T, P for
                           kilobytes, megabytes, gigabytes, terabytes, petabytes

    Returns:
        int: Number of bytes
    """
    if val is None:
        return None

    num, unit = val[:-1], val[-1]
    val = float(num) * {
        'K': 1024,
        'M': 1024 * 1024,
        'G': 1024 * 1024 * 1024,
        'T': 1024 * 1024 * 1024 * 1024,
        'P': 1024 * 1024 * 1024 * 1024 * 1024,
    }[unit.upper()]

    return int(val) # Returning an int, as redis works with ints

class RedisMetrics(object):
    # NOTE: If there is no throttling redis instance the other methods don't do anything
    # NOTE: External process will reset values to zero when the window expires
    # {obj}_metric = current_cost_in_window
    """
    Object for interacting with a Redis instance storing metric data

    NOTE: If there is no throttling Redis instance the methods don't do anything
    NOTE: An external process will reset the metrics to zero when the time window expires

    Redis data format: {obj}_metric = current_usage_in_window
    """

    def __init__(self):
        boss_config = bossutils.configuration.BossConfig()
        if len(boss_config['aws']['cache-throttle']) > 0:
            self.conn = redis.StrictRedis(boss_config['aws']['cache-throttle'],
                                          6379,
                                          boss_config['aws']['cache-throttle-db'])
        else:
            self.conn = None

    def get_metric(self, obj):
        """Get the current metric value for the given object

        Args:
            obj (str): Name of the object for which to get the current metric value

        Returns:
            int: Current metric value or zero if there is no Redis instance or no Redis key
        """
        if self.conn is None:
            return 0

        key = "{}_metric".format(obj)
        resp = self.conn.get(key)
        if resp is None:
            resp = 0
        else:
            resp = int(resp.decode('utf8'))
        return resp

    def add_metric_cost(self, obj, val):
        """Increment the current metric value by the given value for the given object

        NOTE: If there is no Redis instance this method doesn't do anything

        Args:
            obj (str): Name of the object for which to increment the current metric value
            val (float|int): Value by which to increase the current metric value
                             NOTE: Value will be convered into an integer
        """
        if self.conn is None:
            return

        key = "{}_metric".format(obj)
        self.conn.incrby(key, int(val))

class MetricLimits(object):
    """Object for reading metric limits from Vault

    NOTE: Values are read once from Vault on initialization
    """
    def __init__(self):
        vault = bossutils.vault.Vault()
        data = vault.read('secret/endpoint/throttle', 'config')
        data = json.loads(data)

        self.system = data.get('system')
        self.apis = data.get('apis')
        self.users = data.get('users')
        self.groups = data.get('groups')

    def lookup_system(self):
        """Return the current metric limit for the entire system

        Returns:
            int or None
        """
        return parse_limit(self.system)

    def lookup_api(self, api):
        """Return the current metric limit for the given API

        Args:
            api (str): Name of the API to get the metric limit for

        Returns:
            int or None
        """
        return parse_limit(self.apis.get(api))

    def lookup_user(self, user):
        """Return the current metric limit for the given user

        A user's metric limit can either be the value given specifically
        to the user or it can be the maximum metric limit for all of the
        groups that the user is a part of.

        Args:
            user (User): Django user object to get the metric limit for

        Returns:
            int or None
        """
        # User specific settings will override any group based limits
        if user.username in self.users:
            return parse_limit(self.users[user.username])

        # Find the largest limit for all groups the user is a member of
        limits = [parse_limit(self.groups[group.name])
                  for group in user.groups.all()
                  if group.name in self.groups]

        if None in limits:
            return None
        else:
            return max(limits)

class BossThrottle(object):
    """Object for checking if a given API call is throttled

    NOTE: The check_* methods don't add the new cost before checking
          if the current call is throttled, so as to still allow an API
          call that will exceed the limit, in case the limit would
          disallow most API calls

    Attributes:
        user_error_detail (str): Error message if the user is throttled
        api_error_detail (str): Error message if the API is throttled
        system_error_detail (str): Error message if the whole system is throttled
    """
    user_error_detail = _("User is throttled. Expected available tomorrow.")
    api_error_detail = _("API is throttled. Expected available tomorrow.")
    system_error_detail = _("System is throttled. Expected available tomorrow.")

    def __init__(self):
        self.data = RedisMetrics()
        self.limits = MetricLimits()

        boss_config = bossutils.configuration.BossConfig()
        self.topic = boss_config['aws']['prod_mailing_list']
        self.fqdn = boss_config['system']['fqdn']

    def error(self, user=None, api=None, system=None, details=None):
        """Method for notifying admins and raising a Throttle exception

        Notifications are send to the Production Mailing List SNS topic

        Args:
            user (optional[str]): Name of the user, if the user is throttled
            api (optional[str]): Name of the API, if the API is throttled
            system (optional[bool]): If the system is throttled
            details (dict): Information about the API call that will be included
                            in the notification to the administrators

        Raises:
            Throttle: Exception with generic information on why the call was throttled
        """
        if user:
            ex_msg = self.user_error_detail
            sns_msg = "Throttling user '{}': {}".format(user, json.dumps(details))
        elif api:
            ex_msg = self.api_error_detail
            sns_msg = "Throttling API '{}': {}".format(api, json.dumps(details))
        elif system:
            ex_msg = self.system_error_detail
            sns_msg = "Throttling system: {}".format(json.dumps(details))

        client = boto3.client('sns')
        client.publish(TopicArn = self.topic,
                       Subject = 'Boss Request Throttled',
                       Message = sns_msg)

        raise Throttled(detail = ex_msg)

    def check(self, api, user, cost):
        """Check to see if the given API call is throttled

        This is the main BossThrottle method and will call the other check_* methods

        Args:
            api (str): Name of the API call being made
            user (User): Django user making the request
            cost (float|int): Cost of the API call being made

        Raises:
            Throttle: If the call is throttled
        """
        details = {'api': api, 'user': user, 'cost': cost, 'fqdn': self.fqdn}

        self.check_user(user, cost, details)
        self.check_api(api, cost, details)
        self.check_system(cost, details)

    def check_user(self, user, cost, details):
        """Check to see if the user is currently throttled

        NOTE: This method will increment the current metric value by cost
              if not throttled

        Args:
            user (User): Django user making the request
            cost (float|int): Cost of the API call being made
            details (dict): General information about the call to be
                            used when notifying administrators

        Raises:
            Throttle: If the user is throttled
        """
        current = self.data.get_metric(user.username)
        max = self.limits.lookup_user(user)

        if max is None:
            return

        if current > max:
            details['current_metric'] = current
            details['max_metric'] = max
            self.error(user = user, details = details)

        self.data.add_metric_cost(user.username, cost)

    def check_api(self, api, cost, details):
        """Check to see if the API is currently throttled

        NOTE: This method will increment the current metric value by cost
              if not throttled

        Args:
            api (str): Name of the API call being made
            cost (float|int): Cost of the API call being made
            details (dict): General information about the call to be
                            used when notifying administrators

        Raises:
            Throttle: If the API is throttled
        """
        current = self.data.get_metric(api)
        max = self.limits.lookup_api(api)

        if max is None:
            return

        if current > max:
            details['current_metric'] = current
            details['max_metric'] = max
            self.error(api = api, details = details)

        self.data.add_metric_cost(api, cost)

    def check_system(self, cost, details):
        """Check to see if the System is currently throttled

        NOTE: This method will increment the current metric value by cost
              if not throttled

        Args:
            cost (float|int): Cost of the API call being made
            details (dict): General information about the call to be
                            used when notifying administrators

        Raises:
            Throttle: If the system is throttled
        """
        current = self.data.get_metric('system')
        max = self.limits.lookup_system()

        if max is None:
            return

        if current > max:
            details['current_metric'] = current
            details['max_metric'] = max
            self.error(system = True, details = details)

        self.data.add_metric_cost('system', cost)
