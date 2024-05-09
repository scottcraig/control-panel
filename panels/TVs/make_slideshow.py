import os
import shutil
from .._utils import utils, movie_maker_fade
from .._utils.ssh import SSH
from ._utils import mime_types
from .make_new_title import make_title_png


def is_video(file_extension):
    """ file should already have mimetype checked at this point! """
    video_extensions = [".avi", ".mpeg", ".mp4", ".ogv", ".webm", ".mkv"]
    return file_extension.lower() in video_extensions

def make_slideshow(username=None):

    # Get user input
    media_folder = utils.input_styled("Drop folder of media files into window, or enter q to quit: \n")
    if media_folder.lower().strip() == "q":
        return 
    if not os.path.isdir(media_folder):
        print("Not a valid directory")
        return
    username = utils.input_styled("Enter username (firstname.lastname) for folder filenames, or enter q to quit: \n").lower().strip()
    if username == 'q':
        return
    
    media_out_folder_path = os.path.join(utils.OUTPUT_DIR, username)
    if os.path.exists(media_out_folder_path):
        print("There is already a folder in the output folder with the name {}. Move it out of the output folder.".format(username))
        return

    # DO stuff with user input
    os.mkdir(media_out_folder_path)

    make_title_png(username, media_out_folder_path)
    
    for dir_entry in os.scandir(media_folder):

        filepath = os.path.join(media_folder, dir_entry.name)

        filepath_base, ext = os.path.splitext(filepath)

        expected_mime_type = None  # Reset
        try:
            expected_mime_type = mime_types[ext.lower()]
        except KeyError:
            # un supported extension
            expected_mime_type = None
            print(f"{filepath} mime type not supported.\n")
            continue


        # If correct mime type verify integrity of media file
        if utils.verify_mimetype(filepath, expected_mime_type):
            success, fixed_url, ext = utils.verify_image_integrity(filepath, expected_mime_type, ext)
            if success:
                if is_video(ext):
                    shutil.move(fixed_url, os.path.join(utils.OUTPUT_DIR, f"({username}.z.{os.path.basename(fixed_url)})"))
                else:
                    shutil.move(fixed_url, media_out_folder_path)
            else:
                print("Error: problem with media could not be fixed. Skipping {}\n".format(media_folder))
                continue
        else:
            print("Unexpected file extension for {}".format(media_folder))
            continue

        output_name = os.path.join(utils.OUTPUT_DIR, username + ".a.mp4")
        print(output_name)
        movie_maker_fade.movie_maker_fade(images_directory=media_out_folder_path, output_file=output_name)



