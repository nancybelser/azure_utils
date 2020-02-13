import os
import traceback
import pprint
from datetime import datetime, timedelta

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.commerce import UsageManagementClient
from azure.mgmt.subscription import SubscriptionClient

from msrestazure.azure_exceptions import CloudError

def get_credentials():
    #this logic requires that environment variables are set.  Once we get a service principal, we will use
    #those credentials, presumably stored in scrooge config somewhere
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id

def get_locations(credentials, subscription_id):
    subscription_client = SubscriptionClient(credentials)
    locations = subscription_client.subscriptions.list_locations(subscription_id)
    print(subscription_id)
    for location in locations:
        print(location.name)

if __name__ == "__main__":
    credentials, subscription_id = get_credentials()
    print(credentials)
    envDict = {'Infra': 'f34f870e-1eed-4463-9958-09d6c81278f3', 'Dev': '1649ee20-8f97-4941-be59-cb40e8aaafea'}
    #print(envDict)
    for env in envDict.keys():
        subscription_id = envDict[env]
        get_locations(credentials, subscription_id)
