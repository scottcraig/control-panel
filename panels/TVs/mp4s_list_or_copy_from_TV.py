from ._mp4s_utils import choose_TV, choose_files

def mp4s_list_or_copy_from_TV():
    print("This function copies mp4 files to the \"output\" folder from a TV you specify.\n")

    hostname = choose_TV()

    print(choose_files(hostname))

