from network_sim.screens.utils import clear_screen
from network_sim.net_utils import Gateway
import questionary
from tabulate import tabulate


def step_2(step_1_results):
    if step_1_results['gateway_choice'] == 'existing':
        print("step_2_existing_gateway")
        return step_2_existing_gateway(step_1_results)
    else:
        print("step_2_new_gateway")
        return step_2_new_gateway(step_1_results)
    
@clear_screen
def step_2_existing_gateway(step_1_results):
    print("[Add Host Wizard - Step 2 (Existing Gateway)]")
    print("Attach Host to existing Gateway. The Host will be able to communicate with other Hosts attached to this Gateway via LAN.\n")
    print("Available Gateways:")
    if Gateway.gateways:
        table = map(lambda x: [x.id, x.name], Gateway.gateways)
        print(tabulate(table, headers=["ID", "Name"]))
    else:
        print("No Gateways available. Please create a Gateway first.\n")
        print("Press Enter to create a new Gateway.")
        input()
        step_1_results['gateway_choice'] = 'new'
        return step_2_new_gateway(step_1_results)
    
    gateway_info = questionary.form(
        gateway_id = questionary.text("Gateway ID:", validate=lambda x: x in [x.id for x in Gateway.gateways]),
        host_gateway_ip = questionary.text(f"Host '{step_1_results['host_name']}' LAN IP: 192.168.1.[3-255]", validate=lambda x: x.isdigit() and int(x) >= 3 and int(x) <= 255)
    ).ask()
    if not gateway_info:
        print("Aborted. Press Enter to continue.")
        input()
        return None
    gateway_info['host_gateway_ip'] = f"192.168.1.{gateway_info['host_gateway_ip']}"
    gateway_info['gateway_id'] = gateway_info['gateway_id']
    return {**step_1_results, **gateway_info}

@clear_screen
def step_2_new_gateway(step_1_results):
    print("[Add Host Wizard - Step 2 (New Gateway)]")
    print("Attach Host to new Gateway. Used to connect Hosts to each other over LAN. Local Hosts will be able to access remote Hosts through other Gateways through the WAN.")
    next_gateway_id = Gateway.next_device_id
    gateway_info = questionary.form(
        gateway_name=questionary.text("Gateway Name:", validate=lambda x: x != ""),
        host_gateway_ip=questionary.text(f"Host '{step_1_results['host_name']}' LAN IP: 192.168.{next_gateway_id}.[3-255]", validate=lambda x: x.isdigit() and int(x) >= 3 and int(x) <= 255)
    ).ask()
    if not gateway_info:
        print("Aborted. Press Enter to continue.")
        input()
        return None
    gateway_info['host_gateway_ip'] = f"192.168.{next_gateway_id}.{gateway_info['host_gateway_ip']}"
    return {**step_1_results, **gateway_info}