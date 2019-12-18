"""Show consumption details"""


import os
import traceback
import pprint

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.commerce import UsageManagementClient

from msrestazure.azure_exceptions import CloudError


# Azure Datacenter
LOCATION = 'eastus'




def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    print("subscription", subscription_id)
    print(credentials)
    return credentials, subscription_id


def run_example():

    consumption_client = get_client_from_cli_profile(ConsumptionManagementClient)
    usage_client = get_client_from_cli_profile(UsageManagementClient)

    #print("consumption client", consumption_client)

    rates = usage_client.rate_card.get("OfferDurableId eq 'MS-AZR-0017P' and Currency eq 'USD' and Locale eq 'en-US' and RegionInfo eq 'US'")
        #print(rate)
    meters = rates.meters
    meterDict = {}
    for meter in meters:
        print(meter.meter_id, meter.meter_name, meter.unit, meter.meter_rates)
        meterDict[meter.meter_id] = {}

    #print(rates.meters)
    """
    print('\nShow consumption details for subscription')
    for item in consumption_client.usage_details.list("\/subscriptions\/f34f870e-1eed-4463-9958-09d6c81278f3\/"):
        #print("\tProduct: {}".format(item.product))
        print(item.product,",", item.name, ",", item.tags, ",", item.date_property,",", item.frequency, ",", item.charge_type,",")
        #print (item)
    """


if __name__ == "__main__":
    run_example()
