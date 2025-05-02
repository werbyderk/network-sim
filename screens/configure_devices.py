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
    selection = questionary.select("Select an option", choices=[
        questionary.Choice(title="Set up network connection to a Gateway", value="gateway"),
        questionary.Choice(title="Kill host", value="kill"),
    ],
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),  # Selected option color
            ('pointer', 'fg:cyan bold'),   # Arrow color
            ('highlighted', 'fg:cyan bold') # Highlighted option color
        ])).ask()
    if selection == "kill":
        host = next(filter(lambda x: x.id == host_id, Host.hosts))
        if questionary.confirm(f"Kill host '{host.name}'? This will remove the Host from the network and will no longer be reachable by other Hosts.", default=False).ask():
            host.remove()
            print("Host killed. Press Enter to continue.")
            input()
        return
    if selection == "gateway":
        print("Set up network connection to a Gateway")
        gateway_id = questionary.text("Enter the ID of the Gateway to connect to: ", validate=validate_gateway_id).ask()
        if not gateway_id:
            return
        gateway = next(filter(lambda x: x.id == gateway_id, Gateway.gateways))
        host = next(filter(lambda x: x.id == host_id, Host.hosts))
        if questionary.confirm(f"Switch host '{host.name}' to use Gateway '{gateway.name}'? ").ask():
            pass

    

def validate_gateway_id(gateway_id):
    if gateway_id not in map(lambda x: x.id, Gateway.gateways):
        return False
    return True

@clear_screen
def configure_gateway(gateway_id):
    print("[Configure Devices - Gateway]\n")
    print("Unimplemented")
    input()

    