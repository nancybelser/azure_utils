"""Show consumption details"""


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
    print("subscription", subscription_id)
    print(credentials)
    return credentials, subscription_id

def get_rgs(credentials, subscription_id, env):
    resource_client = ResourceManagementClient(credentials, subscription_id)
    print("Resource Groups for subscription" + subscription_id)
    rgDict = {}
    for item in resource_client.resource_groups.list():
        rgDict[item.name] = {}
        print(item.name)
        if bool(item.tags):
            rgDict[item.name] = item.tags

if __name__ == "__main__":
    credentials, subscription_id = get_credentials()

    #get_rate_card(credentials, subscription_id)
    envDict = {'Infra': ''}
    print(envDict)
    print('\nShow consumption details for subscription')
    for env in envDict.keys():
        #subscription_id = envDict[env]
        get_rgs(credentials, 'f34f870e-1eed-4463-9958-09d6c81278f3', env)
