from network_sim.screens.utils import clear_screen
import questionary
import os
from pathlib import Path

STEP_1_TEXT = """Add a Host Machine which can be attached to a Gateway.
Must include a network-enabled Python 3 script which will be executed when the machine starts.
"""

@clear_screen
def step_1():
    print("[Add Host Wizard - Step 1]")
    print(STEP_1_TEXT)
    
    machine_info = questionary.form(
        host_name=questionary.text("Host Name:", validate=lambda x: x != ""),
        host_script=questionary.text("Python 3 Script:", validate=lambda x: x != ""),
        host_deps=questionary.text("Dependencies (requirements.txt):", validate=lambda x: x != ""),
        host_ports=questionary.text("(Optional) Comma separated list of ports to expose:"),
        host_start_cmd=questionary.text("Start Command (i.e. python <script>.py):", validate=lambda x: x != "")
    ).ask()
    if not machine_info:
        print("Aborted. Press Enter to continue.")
        input()
        return None 
    if not validate_form(machine_info):
        print("Invalid input. Press Enter to continue.")
        input()
        return None
        

    gateway_choice = questionary.select(
        "Connect to:",
        choices=[
            questionary.Choice(title="Existing Gateway", value='existing'),
            questionary.Choice(title="New Gateway", value='new'),
            questionary.Choice(title="Cancel", value='cancel')
        ],
        use_indicator=True,  # Shows arrow indicator
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),  # Selected option color
            ('pointer', 'fg:cyan bold'),   # Arrow color
            ('highlighted', 'fg:cyan bold') # Highlighted option color
        ])
    ).ask()
    if not gateway_choice:
        print("Aborted. Press Enter to continue.")
        input()
        return None
    if gateway_choice == 'cancel':
        return None
    machine_info['gateway_choice'] = gateway_choice
    return machine_info


def validate_file(file_path: str) -> bool:
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File '{file_path}' does not exist")
        return False
        
    if not path.is_file():
        print(f"Error: '{file_path}' is not a file")
        return False
        
    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permissions for '{file_path}'")
        return False
        
    return True

def validate_file_path(path: str) -> bool:
    if not path or not validate_file(path):
        return False
    return True

def validate_ports(ports: str) -> bool:
    try:
        # Split and strip whitespace
        port_list = [p.strip() for p in ports.split(',')]
        
        # Check each port is a number between 1-65535
        for port in port_list:
            if port == "":
                continue
            if not port.isdigit():
                print(f"Error: '{port}' is not a number")
                return False
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                print(f"Error: Port {port_num} must be between 1-65535")
                return False
                
        return True
    except Exception:
        return False

def validate_form(answers):
    if not answers:
        return False
    # Validate Python script
    if not validate_file_path(answers['host_script']):
        return False
    # Validate dependencies file
    if not validate_file_path(answers['host_deps']):
        return False
    # Validate ports
    if not validate_ports(answers['host_ports']):
        return False
    return True