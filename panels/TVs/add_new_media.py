import os
from urllib.parse import urlparse

from panels._utils import utils
from panels._utils.ssh import SSH

from panels.TVs.refresh_slideshow import refresh_slideshow

from panels.TVs._utils import mime_types, guess_tv, TV_FILE_SERVER, TV_FILE_SERVER_USER, TV_FILE_SERVER_PW, TV_ROOT

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

        # if starts with a slash then local file
        if media_url[0] != 'C':  # not local
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
            media_url, expected_mime_type, local)

        # If correct mime type verify integrity of media file
        if mime_type_good:
            success, media_url, local, extension = utils.verify_image_integrity(
                media_url, expected_mime_type, local, extension)
            if not success:
                return None, None, None, None

        # returns necessary veriables to continue the code once mime type has been verified
    return media_url, name_without_ext, extension, local


def add_new_media(username=None, tv=None):
    is_quit = False

    username_invalid = True
    media_url = True
    while media_url and username_invalid:
        # gets and checks the url of the file
        media_url, name_without_ext, extension, local = get_media_url()
        if media_url is None:
            return
        elif media_url is "q":
            break

        # collects information to name the file, and as to which tv to send it to
        username_input = utils.input_styled(
            "Enter username (default = {}) or [q]uit: \n".format(username))
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

        tv = guess_tv(username)
        if tv is 'q':
            # restart while loop
            media_url = True
            username_invalid = True
            continue
        tv_input = utils.input_styled(
            "What TV # are you sending this to? (default = {}): ".format(tv))
        if not tv_input:
            if tv_input is None:
                utils.print_error("There is no TV with that name.")
                return

            pass
        else:
            tv = tv_input

        image_name = None
        name_good = utils.input_styled(
            "What is the name of this media? (default = {}): ".format(name_without_ext))
        if not name_good:
            image_name = name_without_ext
        else:
            image_name = name_good

        filename = username + ".z." + image_name + extension

        # Save videos directly in the tv's root directory.
        if is_video(extension.lower()):
            filepath = "{}/tv{}/".format(TV_ROOT, tv)
        # Save images into a subfolder, which will be used to generate a slideshow video
        else:
            filepath = "{}/tv{}/{}/".format(TV_ROOT, tv, username)

        utils.print_warning(
            "Sending {} to hightower to see if file exists already with that name.".format(filename))

        # connects and checks to see if file with the same name already exisits
        ssh_connection = SSH(
            TV_FILE_SERVER, TV_FILE_SERVER_USER, TV_FILE_SERVER_PW)
        already_exists = ssh_connection.file_exists(filepath, filename)

        # if it does exist, asks user if they want to overwrite it
        while already_exists and not utils.confirm(
                "There is a file that already exists with that name. Do you want to overwrite it?",
                yes_is_default=False
        ):
            # don't want to overwrite, so get a new name:
            image_name = utils.input_styled(
                "Provide a different name for the media: ")
            filename = username + ".z." + image_name + extension
            # check again
            already_exists = ssh_connection.file_exists(filepath, filename)

        # make sure the directory exists, if not create it:
        if not ssh_connection.file_exists(filepath):
            ssh_connection.send_cmd('mkdir {}'.format(filepath))

        if local:
            # transfer local file
            # TODO combine this into method with add_new_title() identical code
            local_command = 'sshpass -p "{}" scp {} {}@{}:{}{}'.format(
                TV_FILE_SERVER_PW,
                media_url,
                TV_FILE_SERVER_USER,
                TV_FILE_SERVER,
                filepath, filename
            )

            status = os.system(local_command)
            #  https://docs.python.org/3/library/os.html#os.WEXITSTATUS
            success = os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0

        else:
            # download from web
            command = "wget -O {}{} '{}' && exit".format(
                filepath, filename, media_url)
            success = ssh_connection.send_cmd(command)

        if success:
            utils.print_success(
                "{} was succesfully sent over to pi-tv{}".format(filename, tv))
        else:
            utils.print_error(
                "Something went wrong.  Check the filename, is it wonky with weird characters?")

        # asks user if they want to add another image
        if utils.confirm("Would you like to add another image or video?"):
            media_url = True
            username_invalid = True
        else:
            # close connection here
            ssh_connection.close()
            break

        ssh_connection.close()

    if utils.confirm("Do you want to generate a new video slideshow of this student's art?"):
        # refresh the slideshow
        refresh_slideshow(username=username)
