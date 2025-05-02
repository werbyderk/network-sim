from network_sim.screens.utils import clear_screen
MENU_TITLE = "[Main Menu]\n"
import questionary

@clear_screen
def main_menu():
    print(MENU_TITLE)
    choice = questionary.select(
        "Select an option:",
        choices=[
            questionary.Choice(title="Add Host", value=1),
            questionary.Choice(title="Add Gateway", value=2),
            questionary.Choice(title="List Devices", value=3),
            questionary.Choice(title="Configure Devices", value=4),
            questionary.Choice(title="Exit", value=5)
        ],
        use_indicator=True,  # Shows arrow indicator
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),  # Selected option color
            ('pointer', 'fg:cyan bold'),   # Arrow color
            ('highlighted', 'fg:cyan bold') # Highlighted option color
        ])
    ).ask()
    
    return choice

    