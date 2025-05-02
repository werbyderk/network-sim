from network_sim.screens.utils import clear_screen
from network_sim.net_utils import Gateway, Host
import questionary

@clear_screen
def step_3(usr_input):
    gateway = next((g for g in Gateway.gateways if g.id == usr_input['gateway_id']), None) if usr_input['gateway_choice'] == 'existing' else None
    print("[Add Host Wizard - Step 3]")
    print("The following changes to the network will be made:")
    print(f"- Create Host '{usr_input['host_name']}'")
    print(f"    - Python 3 Script: {usr_input['host_script']}")
    print(f"    - Dependencies: {usr_input['host_deps']}")
    print(f"    - Ports: {usr_input['host_ports']}")
    print(f"    - Start Command: {usr_input['host_start_cmd']}")
    if usr_input['gateway_choice'] == 'new':
        print(f"- Create Gateway '{usr_input['gateway_name']}'")
        print(f"    - Gateway WAN IP: {Gateway.get_next_wan_ip()}")
    print(f"- Connect Host '{usr_input['host_name']}' to Gateway '{gateway.name if gateway else usr_input['gateway_name']}'")
    print(f"    - Host IP: {usr_input['host_gateway_ip']}")
    confirm = questionary.confirm("Proceed?", default=True).ask()
    if confirm:
        host = Host(usr_input['host_name'], 
                    usr_input['host_script'], 
                    usr_input['host_deps'], 
                    list(map(lambda x: int(x), usr_input['host_ports'].split(','))) if usr_input['host_ports'] else [],
                    usr_input['host_start_cmd'])
        gateway = Gateway(usr_input['gateway_name']) if usr_input['gateway_choice'] == 'new' else gateway
        gateway.add_host(host, usr_input['host_gateway_ip'])
        print("Done. Press Enter to continue.")
        input()
    else:
        print("Aborted. Press Enter to continue.")
        input()
    
    
    
