from .._utils.pi import reboot_pi
from .._utils import utils

hostname = "pi-themes"


def turn_tv_pi_off_and_on_again(tv=None):
    if tv is None:
        tv = utils.input_styled("Which TV #? (1-4) ")

    reboot_pi(f'pi-tv{tv}')
