import os
import platform
import sys
import termios
import tty

TITLE = "**Network Simulator**"

def getch():
    """Get a single character from stdin without waiting for Enter."""
    if platform.system() == 'Windows':
        import msvcrt
        return msvcrt.getch().decode('utf-8')
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def clear_screen(fn):
    def wrapper(*args, **kwargs):
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
        print(TITLE)
        return fn(*args, **kwargs)
    return wrapper

    