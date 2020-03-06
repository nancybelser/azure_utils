#!/usr/bin/env python
"""Show consumption details"""


import os
import traceback
import pprint
import psycopg2
import logging
from datetime import date, datetime, timedelta

from scrooge.pricing import POST_SERVICES, add_price, AWS_VENDOR, \
    add_service_translation, find_price, get_term_match_filter
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
startDate = '2020-02-05T00:00:00Z'
endDate = '2020-02-06T00:00:00Z'

DATABASE_URL = os.environ['DATABASE_URL']
envDict = {'Azure Infra': 'f34f870e-1eed-4463-9958-09d6c81278f3', 'Azure Dev': '1649ee20-8f97-4941-be59-cb40e8aaafea'}



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

def get_usage_agg(credentials, subscription_id):
    usage_client = UsageManagementClient(credentials,subscription_id,base_url=None)
    #usage_client = get_client_from_cli_profile(UsageManagementClient)

    #print("consumption client", consumption_client)


    # our offer id is MS-AZR-0017P.
    # MS-AZR-0003P is the on-demand offer id
    print(str(date.today()))
    print(str(date.today() - timedelta(days=1))+'T00:00:00Z')
    #rates = usage_client.usage_aggregates.list(str(date.today() - timedelta(days=1))+'T00:00:00Z',str(date.today())+'T00:00:00Z')
    rates = usage_client.usage_aggregates.list(startDate,endDate)
    print("after")
    for rate in rates:
        #print(rate.usage_start_time, ",", rate.usage_end_time, ",", rate.meter_id, ",", rate.meter_name, ",", rate.meter_category, ",", rate.meter_sub_category, ",", rate.meter_region, ",",rate.unit, ",", rate.quantity)
        print(rate)

if __name__ == "__main__":
    credentials, subscription_id = get_credentials()

    #print(envDict)
    #print('\nShow consumption details for subscription')

    get_usage_agg(credentials, subscription_id)
