import os
from urllib.parse import urlparse

import shutil

from .._utils import utils
from .._utils.ssh import SSH

from ._utils import mime_types

# this code worked on by Nicholas (Tseilorin) Hopkins


def is_video(file_extension):
    """ file should already have mimetype checked at this point! """
    video_extensions = [".avi", ".mpeg", ".mp4", ".ogv", ".webm", ".mkv"]
    return file_extension.lower() in video_extensions


def get_media_url():

    mime_type_good = False
    # creates a loop so it alwasy goes back to the start instead of exiting the code
    while not mime_type_good:
        media_url = utils.input_styled(
            "Paste image (png, jpg) or video (mp4, avi, mpeg, etc.) url, \nor drag and drop a local file into the terminal or [q]uit: \n")

        if media_url == "q":
            return "q", None, None, None

        # if file was pasted in, it may be surrounded in single quotes, remove them:
        if media_url[0] == "'" and media_url[-1] == "'":
            media_url = media_url[1:-1]  # remove first and last characters

        filepath = media_url
        local = True  # assume local by default

        # if starts with a 'c' then local file (e.g. c:\path\to\\file.png) 
        if media_url[0].lower() != 'c':  # not local
            local = False
            # takes url and breaks it into name with no extension, and the extension into variables
            parsed_url_tuple = urlparse(media_url)
            filepath = parsed_url_tuple.path

        name_with_ext = os.path.basename(filepath)
        name_without_ext, extension = os.path.splitext(name_with_ext)

        # verifies mime type
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
            success, media_url, extension = utils.verify_image_integrity(
                media_url, expected_mime_type, extension)
            if not success:
                return None, None, None

        # returns necessary veriables to continue the code once mime type has been verified
    return media_url, name_without_ext, extension


def add_new_media(username=None, tv=None):
    is_quit = False

    username_invalid = True
    media_url = True
    while media_url and username_invalid:
        # gets and checks the url of the file
        media_url, name_without_ext, extension = get_media_url()
        if media_url is None:
            print("Problem with media file.\n")
            return
        elif media_url is "q":
            break
        print(media_url)
        # collects information to name the file, and as to which tv to send it to
        username_input = utils.input_styled(
            "Enter username (firstname.lastname) (default = {}) or [q]uit: \n".format(username))
        if not username_input:
            pass
        else:
            username = username_input

        if username is None:
            utils.print_warning("Please enter a valid username")
            return
        elif username == "q":
            break
        else:
            username_invalid = False

        image_name = None
        name_good = utils.input_styled(
            "What is the name of this media? (default = {}): ".format(name_without_ext))
        if not name_good:
            image_name = name_without_ext
        else:
            image_name = name_good.replace(" ", "_")

        filename = username + ".z." + image_name + extension
        out_filepath = os.path.join(utils.OUTPUT_DIR, filename)
        shutil.copy(media_url, out_filepath)



