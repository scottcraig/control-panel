import os
import shutil
from .._utils import utils, movie_maker_fade
from .._utils.ssh import SSH
from ._utils import mime_types
from .make_new_title import make_title_png


def make_slideshow(username=None):

    # Get user input
    media_url = utils.input_styled("Drop folder of media files into window, or enter q to quit: \n")
    if media_url.lower().strip() == "q":
        return 
    if not os.path.isdir(media_url):
        print("Not a valid directory")
        return
    username = utils.input_styled("Enter username (firstname.lastname) for folder filenames, or enter q to quit: \n").lower().strip()
    if username == 'q':
        return
    
    media_out_folder_path = os.path.join(utils.OUTPUT_DIR, username)
    if os.path.exists(media_out_folder_path):
        print("There is already a folder in the output folder with the name {}. Move it out of the output folder.".format(username))
        return

    fullname = utils.input_plus("Enter the name to appear in the title card, or enter q to quit: ")
    if fullname.lower().strip() == "q":
        return
    grad_year = utils.input_plus("Grad Year, or enter q to quit: ")
    if grad_year.lower().strip() == "q":
        return

    # DO stuff with user input
    os.mkdir(media_out_folder_path)

    make_title_png(username, fullname, grad_year, media_out_folder_path)
    
    for file in os.scandir(media_url):
        expected_mime_type = None  # Reset
        try:
            expected_mime_type = mime_types[extension.lower()]
        except KeyError:
            # un supported extension
            expected_mime_type = None

        # checks if file is what it really says it is
        mime_type_good = utils.verify_mimetype(
            media_url, expected_mime_type)

        # If correct mime type verify integrity of media file
        if mime_type_good:
            success, fixed_url, extension = utils.verify_image_integrity(media_url, expected_mime_type, extension)
            if success:
                shutil.move(fixed_url, media_out_folder_path)
            else:
                print("Error: problem with media could not be fixed. Skipping {}\n".format(media_url))
                break
        else:
            print("Unexpected file extension for {}".format(media_url))
            break

        output_name = os.path.join(utils.OUTPUT_DIR, username + ".a.mp4")
        movie_maker_fade.movie_maker_fade(images_directory=media_out_folder_path, output_file=output_name)



