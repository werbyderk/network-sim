from network_sim.screens.utils import clear_screen, getch
from network_sim.net_utils import Gateway
from tabulate import tabulate

@clear_screen
def list_devices():
    print('[List Devices]\n')

    table = []
    for gateway in Gateway.gateways:
        table.append([gateway.id, gateway.name])
        for host in gateway.hosts:
            table.append([host.id, host.name])
    print(tabulate(table, headers=["ID", "Name"]))
    print("\nPress d for detailed view, or any other key to continue.")
    if getch() == 'd':
        list_detailed_devices()

@clear_screen
def list_detailed_devices():
    print('[List Devices - Detailed]\n')

    table = []
    for gateway in Gateway.gateways:
        table.append([gateway.id, gateway.name, 'Gateway', gateway.wan_ip, gateway.lan_ip, 'N/A', 'N/A'])
        for host in gateway.hosts:
            table.append([host.id, host.name, 'Host', 'N/A', host.ip, gateway.id, ','.join(map(str, host.ports)) if host.ports else 'None'])
    
    print(tabulate(table, headers=["ID", "Name", "Type", "WAN IP", "LAN IP", "Connected to", "Exposed Ports"]))
    print("\nPress Enter to continue.")
    input()