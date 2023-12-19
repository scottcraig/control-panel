
import os
import sys
from collections import OrderedDict
# from importlib import import_module
from pip._internal import main as pipmain

from panels._utils import utils
# from panels import themes

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
PANELS_DIR = "panels"


def load_modules():
    # https://stackoverflow.com/a/951678/2700631
    module_dir = PANELS_DIR
    # panels_dir += (os.sep + module_name) if module_name else ''
    module_dict = {}
    # check subfolders
    lst = os.listdir(module_dir)
    directories = []
    lst = [s for s in lst if s[0] not in "_."]  # remove hidden modules
    for d in lst:
        s = os.path.abspath(module_dir) + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + "__init__.py"):
            directories.append(d)
    # load the modules
    for d in directories:
        module_dict[d] = __import__(module_dir + "." + d, fromlist=["*"])

    # sort by key
    return OrderedDict(sorted(module_dict.items()))


def load_panels(module):
    panels_dir = PANELS_DIR + os.sep + module
    panels = os.listdir(panels_dir)
    panels = [s for s in panels if s[0] not in "_."]  # remove hidden files
    panels = [s[:-3] for s in panels]  # remove '.py'
    panel_dict = {}
    module_dir = PANELS_DIR

    for p in panels:
        panel_dict[p] = __import__(
            module_dir + "." + module + "." + p, fromlist=["*"])

    # sort by key
    return OrderedDict(sorted(panel_dict.items()))


def print_menu(menu_items, title, quit_option=True, back_option=False):
    os.system('clear')
    utils.print_heading(title)

    for i, item in enumerate(menu_items):
        print("{}. {}".format(i, item))

    if back_option:
        print("[b]ack")

    if quit_option:
        print("[q]uit")

    choice = input("\nChoose an item: ")

    return choice


def pip_install():
    utils.print_warning(
        "Checking to see if all necassary pip modules are installed. \n")
    pipmain(['install', 'paramiko'])
    pipmain(['install', 'inquirer'])
    utils.print_success("Everything is installed!")
    os.system('clear')


def control_panel():

    try:
        # get modules
        module_dict = load_modules()

        # pip_install()  # use requirements.txt

        while True:
            menu_items = list(module_dict.keys())
            menu_choice = print_menu(menu_items, "Hackerspace Control Panel")

            if menu_choice == 'q':
                break

            try:
                module_choice = menu_items[int(menu_choice)]

                # add b as a menu option so you can go back to the previous menu / when done with a certain menu have it go back to the same menu it came from (C said while loop)

                # get panels from chosen module
                sub_module_dict = load_panels(module_choice)
                menu_items = list(sub_module_dict.keys())

                sub_module_choice_str = print_menu(
                    menu_items, module_choice, back_option=True)

                if sub_module_choice_str == 'q':
                    break

                if sub_module_choice_str == 'b':
                    continue

                sub_module_key = menu_items[int(sub_module_choice_str)]

            except ValueError:
                input(
                    "\nBleep bloop, sorry, I didn't understand that.  Can you speak slower? I'm just a simple menu...[hit Enter to continue]\n")

                continue
            except IndexError:
                input(
                    "\nDude, that wasn't an option, please read the menu more carefully, thanks! [hit Enter to continue]")
                continue

            sub_module = sub_module_dict[sub_module_key]

            method = getattr(sub_module, sub_module_key)
            os.system('clear')
            title = "{} > {}".format(module_choice, sub_module_key)
            utils.print_heading(title)
            method()
            input("Hit Enter to continue. ")

    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        print("\nGoodbye")


control_panel.current_module = 'panels'


if __name__ == '__main__':
    control_panel()
