"""Create and manage virtual machines.

This script expects that the following environment vars are set:

AZURE_TENANT_ID:
AZURE_CLIENT_ID:
AZURE_CLIENT_SECRET:
AZURE_SUBSCRIPTION_ID:
"""
import os
import traceback

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.common.client_factory import get_client_from_cli_profile

from msrestazure.azure_exceptions import CloudError


# Azure Datacenter
LOCATION = 'eastus'

# Resource Group
GROUP_NAME = 'azure-sample-group-virtual-machines'

# Network
VNET_NAME = 'azure-sample-vnet'
SUBNET_NAME = 'azure-sample-subnet'

# VM
OS_DISK_NAME = 'azure-sample-osdisk'

IP_CONFIG_NAME = 'azure-sample-ip-config'
NIC_NAME = 'azure-sample-nic'
USERNAME = 'userlogin'
PASSWORD = 'Pa$$w0rd91'
VM_NAME = 'VmName'

VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServer',
        'offer': 'WindowsServer',
        'sku': '2016-Datacenter',
        'version': 'latest'
    }
}


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
    """Virtual Machine management example."""
    #
    # Create all clients with an Application (service principal) token provider
    #
    #credentials, subscription_id = get_credentials()
    #resource_client = ResourceManagementClient(credentials, subscription_id)
    resource_client = get_client_from_cli_profile(ResourceManagementClient)
    #compute_client = ComputeManagementClient(credentials, subscription_id)
    compute_client = get_client_from_cli_profile(ComputeManagementClient)
    #network_client = NetworkManagementClient(credentials, subscription_id)

    print("compute client", compute_client)

    # List VMs in subscription
    print('\nList VMs in subscription')
    for vm in compute_client.virtual_machines.list_all():
        print("\tVM: {}".format(vm.name))
        print (vm)

    print('\nList Resources in subscription')
    for item in resource_client.resource_groups.list():
        print(item)

if __name__ == "__main__":
    run_example()
