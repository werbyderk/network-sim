from network_sim.screens.utils import clear_screen
import questionary
from network_sim.net_utils import Gateway, Host

@clear_screen
def configure_devices():
    print("[Configure Devices]\n")
    print("Select a Host or Gateway to set up network connections")
    choice = questionary.text("Enter the ID of the device to configure: ", validate=validate_device_id).ask()
    if not choice:
        return
    if choice[0] == 'h':
        configure_host(choice)
    elif choice[0] == 'g':
        configure_gateway(choice)
    return choice

def validate_device_id(device_id):
    if device_id not in map(lambda x: x.id, Gateway.gateways) and device_id not in map(lambda x: x.id, Host.hosts):
        return False
    return True

@clear_screen
def configure_host(host_id):
    print("[Configure Devices - Host]\n")
    print("Set up network connection to a Gateway")
    gateway_id = questionary.text("Enter the ID of the Gateway to connect to: ", validate=validate_gateway_id).ask()
    if not gateway_id:
        return
    gateway = next(filter(lambda x: x.id == gateway_id, Gateway.gateways))
    host = next(filter(lambda x: x.id == host_id, Host.hosts))
    if questionary.confirm(f"Switch host '{host.name}' to use Gateway '{gateway.name}'? ").ask():
        pass

    input()

def validate_gateway_id(gateway_id):
    if gateway_id not in map(lambda x: x.id, Gateway.gateways):
        return False
    return True

@clear_screen
def configure_gateway(gateway_id):
    print("[Configure Devices - Gateway]\n")
    print("Unimplemented")
    input()

    