import logging
import os

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

VM_NAME = os.environ["AZURE_VM_NAME"]
GROUP_NAME = os.environ["AZURE_GROUP_NAME"]
STATUS_RUNNING = "VM running"

logger = logging.getLogger(__name__)


async def wake_up_worker():
    try:
        await __try_to_wake_up_worker()
    except Exception as e:
        logger.error(str(e))


async def __try_to_wake_up_worker():
    credentials, subscription_id = __get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    initial_vm_info = __get_virtual_machine_info(compute_client)

    if __get_vm_status(initial_vm_info) == STATUS_RUNNING:
        logger.info("VM already running")
        return

    logger.info("Starting virtual machine")
    vm_start = compute_client.virtual_machines.begin_start(GROUP_NAME, VM_NAME)
    vm_start.wait()
    logger.info("Virtual machine running")
    final_vm_info = __get_virtual_machine_info(compute_client)
    logger.info(f"VM Status: {__get_vm_status(final_vm_info)}")


def __get_credentials():
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    credentials = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )
    return credentials, subscription_id


def __get_virtual_machine_info(compute_client: ComputeManagementClient):
    return compute_client.virtual_machines.instance_view(GROUP_NAME, VM_NAME)


def __get_vm_status(vm_info):
    return vm_info.statuses[1].display_status
