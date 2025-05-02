from network_sim.net_utils import Gateway
import questionary 
from network_sim.screens.utils import clear_screen

@clear_screen
def add_gateway():
    print("[Add Gateway]\n")
    print("Create a new Gateway. Used to connect Hosts to each other over LAN. Local Hosts will be able to access remote Hosts through other Gateways through the WAN.\n")
    gateway_name = questionary.text("Gateway Name:").ask()
    print(f"Ready to create Gateway '{gateway_name}'.")
    confirm = questionary.confirm("Proceed?", default=True).ask()
    if confirm:
        Gateway(gateway_name)
        print(f"Done. Press Enter to continue.")
        input()
    else:
        print("Aborted. Press Enter to continue.")
        input()
    
