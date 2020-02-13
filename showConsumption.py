"""Show consumption details"""


import os
import traceback
import pprint
from datetime import datetime, timedelta

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.commerce import UsageManagementClient

from msrestazure.azure_exceptions import CloudError


# Azure Datacenter
#LOCATION = 'eastus'
GRANULARITY = "DAILY"
DATE_STRING = "%Y-%m-%d"
startDate = '2020-02-03T00:00:00Z'
endDate = '2020-02-04T23:59:59Z'




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

def get_rate_card(credentials, subscription_id):
    usage_client = UsageManagementClient(credentials,subscription_id,base_url=None)
    #usage_client = get_client_from_cli_profile(UsageManagementClient)

    #print("consumption client", consumption_client)


    # our offer id is MS-AZR-0017P.
    # MS-AZR-0003P is the on-demand offer id
    rates = usage_client.rate_card.get("OfferDurableId eq 'MS-AZR-0003P' and Currency eq 'USD' and Locale eq 'en-US' and RegionInfo eq 'US'")
    #print(rates)
    meters = rates.meters
    meterDict = {}
    for meter in meters:
        print(meter.meter_id, meter.meter_name, meter.unit, meter.meter_rates)
        meterDict[meter.meter_id] = {}

    #print(rates.meters)


def get_consumption(credentials, subscription_id, env):
    resource_client = ResourceManagementClient(credentials, subscription_id)
    print("Resource Groups for subscription" + subscription_id)
    rgDict = {}
    for item in resource_client.resource_groups.list():
        name = (item.name).lower()
        rgDict[name] = {}
        #print(name)
        if bool(item.tags):
            rgDict[name] = item.tags
    #print(rgDict)
    consumption_client = ConsumptionManagementClient(credentials,subscription_id,base_url=None)

    scope = "\/subscriptions\/" + subscription_id + "\/"
    #print(scope)
    date_filter ='usageStart gt '+ str('2020-02-03T00:00:00Z')
    #print(date_filter)

    #for item in consumption_client.usage_details.list("\/subscriptions\/f34f870e-1eed-4463-9958-09d6c81278f3\/", metric='AmortizedCostMetricType'):    #for item in consumption_client.usage_details.list("\/subscriptions\/f34f870e-1eed-4463-9958-09d6c81278f3\/"):
    #for item in consumption_client.usage_details.list(scope, filter=date_filter):
    for item in consumption_client.usage_details.list(scope):
        #print(item.resource_group)
        #print(item.name + " " + item.resource_group.lower())
        rg = rgDict.get(item.resource_group.lower())
        #print(rg)
        #print(item)
        #print(item.date_property,",", item.resource_group.lower(), ",", item.meter_id, ",", item.name, ",", item.product,",", item.quantity, ",", item.effective_price, ",", item.cost,",", item.unit_price)
        #print(item.date_property,",", item.resource_group.lower(), ",", item.meter_details, ",", item.name, ",", item.product,",", item.consumed_service, ",", item.resource_name, ",", item.resource_location, "," ,item.unit_price, )
        print(item.date_property,",", item.resource_group.lower(), ",", item.resource_id, ",", item.name, ",", item.product,",", item.consumed_service, ",", item.resource_name, ",", item.resource_location, ",", item.unit_price, ",", item.quantity )



if __name__ == "__main__":
    credentials, subscription_id = get_credentials()

    #get_rate_card(credentials, subscription_id)
    envDict = {'Infra': 'f34f870e-1eed-4463-9958-09d6c81278f3', 'Dev': '1649ee20-8f97-4941-be59-cb40e8aaafea'}
    #print(envDict)
    #print('\nShow consumption details for subscription')
    for env in envDict.keys():
        subscription_id = envDict[env]
        get_consumption(credentials, subscription_id, env)
