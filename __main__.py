from network_sim.screens.launch_screen import launch_screen
from network_sim.screens.main_menu import main_menu
from network_sim.screens.add_host.step_1 import step_1 as add_host_step_1
from network_sim.screens.add_host.step_2 import step_2 as add_host_step_2
from network_sim.screens.add_host.step_3 import step_3 as add_host_step_3
from network_sim.net_utils import Gateway
from network_sim.screens.add_gateway import add_gateway
from network_sim.screens.list_devices import list_devices
from network_sim.screens.configure_devices import configure_devices

if __name__ == "__main__":
    launch_screen()
    while True:
        submenu = main_menu()
        match submenu:
            case 1:
                usr_input = add_host_step_1()
                if usr_input:
                    usr_input = add_host_step_2(usr_input)
                    if usr_input:
                        add_host_step_3(usr_input)
            case 2:
                add_gateway()
            case 3:
                list_devices()
            case 4:
                configure_devices()
            case 5:
                print("Shutting down...")
                while Gateway.gateways:
                    Gateway.gateways[0].remove()
                if Gateway.wan:
                    Gateway.wan.remove()
                break
