
from ._mp4s_utils import choose_TV


def mp4s_push_to_TV():
    print("This function pushes any mp4 files in the \"output\" folder to a TV you specify.\n")

    hostname = choose_TV()

    print(hostname)