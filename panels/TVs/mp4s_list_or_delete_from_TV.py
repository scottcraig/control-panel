
from ._mp4s_utils import choose_TV, choose_files

def mp4s_list_or_delete_from_TV():
    print("This function delets mp4 files from a TV you specify.\n")

    tv = choose_TV()

    print(choose_files(tv))