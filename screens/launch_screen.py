from network_sim.screens.utils import clear_screen
MENU_TITLE = "[Welcome]\n"
LAUNCH_SCREEN_TEXT= """The Network Simulator can help simulate loads and network conditions for your application.
By adding Hosts to a Gateway, machines can talk with each other via LAN or to remote machines with simulate latency and packet loss.

Press Enter to continue."""

@clear_screen
def launch_screen():
    print(MENU_TITLE)
    print(LAUNCH_SCREEN_TEXT)
    input()
