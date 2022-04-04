"""Show consumption details"""


import os
import traceback
import pprint
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
import argparse


#from ..utils import AWS_REGIONS, daterange
#from ..scrooge import get_collected_metrics, add_cost, get_metric_ids, ONDEMAND, DISCOUNTED, USAGE, USD
#from . import with_connection, get_task_logger, PROFILE_NAME_KEY
#from ..tag import get_tag_keys, get_tag_id, add_tag
from scrooge.api.service.org_service import get_org
from scrooge.api.service.region_service import get_region_id, get_region_id_add_ifnone
from scrooge.api.service.account_service import get_account, get_accounts
from scrooge.constants import DEFAULT_BOTO_CONFIG
from scrooge.api.service import service_service
from scrooge.pricing import get_azure_price
from scrooge.tag import get_tag_keys, get_tag_id, add_tag
from scrooge.scrooge import get_collected_metrics, add_cost, get_metric_ids, ONDEMAND, DISCOUNTED, USAGE, USD

#from ..pricing import get_price, SERVICE_VERSIONS, AZURE_VENDOR

from scrooge.api.model.ecosystem import Ecosystem

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.commerce import UsageManagementClient
from azure.mgmt.subscription import SubscriptionClient

from msrestazure.azure_exceptions import CloudError


# Azure Datacenter
#LOCATION = 'eastus'
GRANULARITY = "DAILY"
DATE_STRING = "%Y-%m-%d"
startDate = '2020-02-23T00:00:00'
endDate = '2020-02-24T23:59:59'
usageEndDate = '2020-02-15T00:00:00Z'

AZURE_REGIONS = {'US East': 'eastus',
                'US West 2': 'westus2',
                'US West': 'westus',
                'US East 2': 'eastus2',
                'Zone 1':  'zone1'}

AZURE_ECOSYSTEM_PREFIX="GenesysEngage%"
ORG_ID=2
DATABASE_URL = os.environ['DATABASE_URL']



def get_credentials():
    #this logic requires that environment variables are set.  Once we get a service principal, we will use
    #those credentials, presumably stored in scrooge config somewhere
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    #print("subscription", subscription_id)
    #print(credentials)
    return credentials, subscription_id

def get_consumption(conn, credentials, subscription_id, account_id, org, start_date, end_date):
    cur = conn.cursor()
    resource_client = ResourceManagementClient(credentials, subscription_id)
    print("Resource Groups for subscription" + subscription_id)
    tagGroupDict = {}

    for index_tag_group, tag_group in enumerate(get_tag_keys(conn, org_id=org['org_id']), 1):
    #    print(index_tag_group, tag_group)
        tagGroupDict[tag_group['name']] = tag_group['tag_group_id']
    print(tagGroupDict)
    rgDict = {}
    for item in resource_client.resource_groups.list():
        name = (item.name).lower()
        rgDict[name] = {}
        if bool(item.tags):
            rgDict[name] = item.tags
    #date = datetime.datetime.now()
    #print(rgDict)

    consumption_client = ConsumptionManagementClient(credentials,subscription_id,base_url=None)

    scope = "\/subscriptions\/" + subscription_id + "\/"
    #print(scope)
    #date_filter ='usageEnd le '+ str(usageEndDate)
    date_filter = "properties/usageStart ge " + "\'" + start_date + "\'" + " AND properties/usageStart lt " + "\'" + end_date + "\'"
    print(date_filter)

    #'''
    #for item in consumption_client.usage_details.list("\/subscriptions\/f34f870e-1eed-4463-9958-09d6c81278f3\/", metric='AmortizedCostMetricType'):    #for item in consumption_client.usage_details.list("\/subscriptions\/f34f870e-1eed-4463-9958-09d6c81278f3\/"):
    cost_sum = 0
    counter = 0
    unique_resource_counter = {}
    for item in consumption_client.usage_details.list(scope, filter=date_filter, expand='additionalInfo'):
    #for item in consumption_client.usage_details.list(scope):
        #print(item.resource_group)
        #print(item.name + " " + item.resource_group.lower())
        metrics_ids = get_metric_ids(conn)
        region_id = get_region_id(conn, item.resource_location.lower())
        row = get_azure_price(conn, item.meter_id)
        unit_list_price = row[0]
        service_id = row[1]
        unit_type = row[2]
        values = {}
        units = {}
        #print("date", item.date_property, "qty: ", item.quantity, "unit_list_price", unit_list_price, "effective_price", item.effective_price, "cost", item.cost, "list cost ", unit_list_price * float(item.quantity))
        values[ONDEMAND] = unit_list_price * float(item.quantity)
        units[ONDEMAND] = USD
        values[DISCOUNTED] = item.cost
        units[DISCOUNTED] = USD
        values[USAGE] = item.quantity
        units[USAGE] = unit_type
        cost_sum += item.cost
        counter += 1
        #print("Resource", item.resource_name, item.resource_id, "Cost", item.cost, "VMName")
        vm_name = ""
        print("----------------------------")
        #print("Item:",item)
        if item.additional_info:
            if 'VMName' in item.additional_info:
                #print("additional", item.additional_info)
                addtl_info = item.additional_info.strip('{').strip('}').replace('"', '').replace(' ', '')
                #print(addtl_info)
                res = dict(x.split(':') for x in addtl_info.split(','))
                #res = dict(map(lambda x: x.split(':'), addtl_info.split(', ')))
                #print(res['VMName'])
                vm_name = res['VMName']
                #for item_row in dict(item.additional_info):
                #    print("item:", item_row)

                #for k, v in info.items():
                #    print(k,v)
                #print(item.additional_info["VMName"])

        tagValues = {}
        for tag_group in tagGroupDict.items():
            #print(tag_group[1])
            tagValues[tag_group[1]] = "unset"
        #print(tagValues)
        rg_tags = rgDict.get(item.resource_group.lower())
        if rg_tags:
            print("rg_tags:", rg_tags)
            for tag in rg_tags.keys():
                tag_value = rg_tags[tag]
                tag_row = tagGroupDict.get(tag)
                #print("tag row", tag_row)
                if tag_row != None:
                    print("tag group row", tag, tag_row, "tag value", tag_value)
                    tagValues[tag_row] = tag_value
        #print(type(tagValues), tagValues)

        for tag_group_id, tag_value in tagValues.items():
            tag_id = get_tag_id(conn, tag_value, tag_group_id)
            print("tag_id", tag_id)
            if not tag_id:
                tag_id = add_tag(
                    conn, tag_value, tag_group_id, org['default_team_id'],
                    org['default_email'], last_seen=datetime.now())
            item_name = item.product + ": " + item.resource_group + ": " + item.resource_name
            if vm_name:
                item_name = item_name + ": " + vm_name
            id_string = (str(account_id) + str(region_id) + str(service_id) + item_name + str(tag_id) + str(item.date_property)).replace(" ", "")
            id_hash = hash(id_string)
            counter_val = unique_resource_counter.get(id_hash)
            if counter_val:
                counter_val += 1
            else:
                counter_val = 1
            unique_resource_counter[id_hash] = counter_val
            item_name = item_name + ":c" + str(counter_val)
            print(id_string, id_hash, counter_val, item_name)
            for k, v in values.items():
                #for meter in item.meter_details:
                #print(type(item.meter_details))
                #item_name = item.meter_details.meter_sub_category +':' + item.meter_details.meter_name +':' + item.resource_name + item.resource_id

                print(account_id, region_id, service_id, item_name, tag_id, item.date_property, metrics_ids[k], v, units[k])
                add_cost(cur, account_id, region_id, service_id, item_name, tag_id, item.date_property, metrics_ids[k], v, units[k])
    print("Subscription", subscription_id, "Cost Summary", cost_sum, "Count", counter)

        #    subscription_id = envDict[env]
        #print(item.resource_location.lower(), region_id, unit_list_price, service, rg_tags)
        #region_id = get_region_id_add_ifnone(conn, item.region_desc, item.resource_location)
        #print(rg)
        #print(item)
        #print(item.date_property,",", item.resource_group.lower(), ",", item.meter_id, ",", item.name, ",", item.product,",", item.quantity, ",", item.effective_price, ",", item.cost,",", item.unit_price)
        #print(item.date_property,",", item.resource_group.lower(), ",", item.meter_details, ",", item.name, ",", item.product,",", item.consumed_service, ",", item.resource_name, ",", item.resource_location, "," ,item.unit_price, )
        #print(item.date_property,",", item.resource_group, ",", item.resource_id, ",", item.meter_id, ",", item.name, ",", item.product,",", item.consumed_service, ",", item.resource_name, ",", item.resource_location, ",", item.unit_price, ",", item.quantity )
        #'''
# subscriptions for azure are stored in the accounts table
def get_subscriptions(conn, org_id):
    def accounts_query(query, args):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, args)
        rows = cur.fetchall()
        details = []
        for row in rows:
            print(row[0], row[1])
        return rows

    return accounts_query(
        """
          SELECT a.account_id, a.account
          FROM eco_systems e, accounts a
          WHERE
          org_id = %(org_id)s
		  AND e.eco_system_id = a.eco_system_id
          AND eco_system LIKE (eco_system)
          ORDER BY account_id
        """
        , {'org_id': org_id, 'eco_system': AZURE_ECOSYSTEM_PREFIX}
    )

def get_locations(conn, credentials, subscription_id):
    subscription_client = SubscriptionClient(credentials)
    locations = subscription_client.subscriptions.list_locations(subscription_id)
    #print(subscription_id)
    for location in locations:
        region_id = get_region_id_add_ifnone(conn, location.name, location.display_name)
        #print(region_id, location.name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--org_id", required=True)
    parser.add_argument("-s", "--start_date", type=str, required=True)
    parser.add_argument("-e", "--end_date", type=str)
    args = parser.parse_args()
    print("args", args)
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    credentials, subscription_id = get_credentials()
    # ORG_ID
    if 'org_id' not in args:
        org_id = ORG_ID
    else:    #raise Exception('org_id required but not specified')
        org_id = args.org_id
    org = get_org(conn, org_id=org_id)


    # DATES

    start_date = datetime.strptime(args.start_date, DATE_STRING)
    end_date = start_date
    if args.end_date:
        end_date = datetime.strptime(args.end_date, DATE_STRING)

    print(start_date, end_date)

    #get_rate_card(credentials, subscription_id)
    #envDict = {'Infra': '', 'Dev': ''}
    print("org", org, "org_id", org_id)
    accounts = get_subscriptions(conn, org_id)
    sub_id = accounts[0][1]
    #get_locations(conn, credentials, sub_id)
    #print(eco_systems)
    #print(envDict)
    #print('\nShow consumption details for subscription')

    for account in accounts:
        print(account[1],account[0])
        get_consumption(conn, credentials, account[1], account[0], org, args.start_date, args.end_date)
