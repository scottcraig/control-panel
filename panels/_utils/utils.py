import io
# import pwd
from getpass import getpass
from typing import Union, Tuple

import PIL
import magic
import imageio.v2 as imageio
from urllib.error import URLError
from urllib.request import urlopen
import subprocess
from PIL import Image, ImageSequence
import moviepy.editor as mp
import urllib.request

import os

# from getpass import getpass

LOCALDOMAIN = "hackerspace.tbl"

# Location constants
FFMPEG = os.path.join("C:", "Program Files",
                      "Krita (x64)", "bin", "ffmpeg.exe")
INKSCAPE = os.path.join("C:", "Program Files",
                        "Inkscape", "bin", "inkscapecom.com")
WIN_TMP = os.getenv("TMP")


class ByteStyle:
    HEADER = '\033[95m'  # intense purple
    SUCCESS = '\033[92m'  # intense green
    WARNING = '\033[93m'  # intense yellow
    ERROR = '\033[91m'  # intense red
    ENDC = '\033[0m'  # resets
    BOLD = '\033[1m'  # makes it bold
    UNDERLINE = '\033[4m'  # underlines
    INPUT = '\033[1;33m'  # bold yellow
    # Y_N = '\033[0;33m'  # dark yellow (brown)
    Y_N = '\033[36m'  # cyan


def print_styled(text, color):
    print(color + text + ByteStyle.ENDC)


def print_success(text):
    print_styled(text, color=ByteStyle.SUCCESS)


def print_warning(text):
    print_styled(text, color=ByteStyle.WARNING)


def print_error(text):
    print_styled(text, color=ByteStyle.ERROR)


def input_styled(text, color=ByteStyle.INPUT):
    return input(color + text + ByteStyle.ENDC).strip()


def print_heading(title):
    width = 60
    title = title.upper()
    if len(title) > width - 4:
        title = title[:width - 7] + "..."
    print_styled("#" * width, color=ByteStyle.HEADER)
    print_styled("#" + title.center(width - 2, " ") +
                 "#", color=ByteStyle.HEADER)
    print_styled("#" * width, color=ByteStyle.HEADER)
    print()


# simple wrapper over common method
def get_computers_prompt(hostname=None, password=None):
    if password is None:
        password = getpass("Enter the admin password: ")

    if hostname is None:
        hostname = input_styled("Enter the computer numbers or name, seperated by spaces \n"
                                "(where # is from hostname tbl-h10-#-s e.g: test 2 15 30)\n"
                                " or 'all' to run on all computers or [q]uit: ")

    if hostname == "q":
        print("Quitting this.")
        return None, None

    num_list = hostname.split()

    if num_list == "":
        return

    if num_list[0].lower() == "all":
        # list of strings.  0 will cause problem if int instead of str
        num_list = [f"{i}" for i in range(0, 32)]

    return num_list, password


def verify_mimetype(file_url, mimetype_string, local=False):
    mt = ''

    if mimetype_string is None:
        print_error(" This media type is not supported.")
        return False

    file_url = file_url.strip()

    if local:
        try:
            mt = magic.from_file(file_url, mime=True)
        except FileNotFoundError as e:
            print("Can't find this file.")
            print_error(str(e))
    else:  # web url
        try:
            with urlopen(file_url) as response:
                mt = response.info().get_content_type()
        except ValueError as e:
            print_error(str(e))
        except URLError as e:
            print("That is a bad URL.")
            print_error(str(e))

    if mt == mimetype_string:
        print_success(f"File looks good: {mt}")
        return True
    else:
        print_error(
            f"Something is funky about this file. I expected type '{mimetype_string}' but got '{mt}'.")
        return False


def is_ffmpeg_compatible(file_url) -> bool:
    """
    Checks to see if the file (local and non-local) is compatible with ffmpeg.
    :returns: success
    """
    command = FFMPEG + " -y -v error -i " + file_url + \
        os.path.join(WIN_TMP, "verify-ffmpeg.mp4")
    err = subprocess.run(command.split(" "), capture_output=True).stderr
    return err == b''


def find_gif_duration(img_obj) -> float:
    """
    Returns duration of gif in seconds
    """
    img_obj.seek(0)  # move to the start of the gif, frame 0
    tot_duration = 0
    # run a while loop to loop through the frames
    while True:
        try:
            # returns current frame duration in milli sec.
            frame_duration = img_obj.info['duration']
            tot_duration += frame_duration
            # now move to the next frame of the gif
            img_obj.seek(img_obj.tell() + 1)  # image.tell() = current frame
        except EOFError:
            return tot_duration / 1000  # this will return the tot_duration of the gif


def remove_gif_transparency(image, file_url) -> str:
    """
    Removes the transparent background of a gif and replaces it with black
    :returns: file_url
    """

    frames = []
    for frame in ImageSequence.Iterator(image):
        # Convert the transparency information to a boolean mask
        alpha = frame.split()[-1].point(lambda x: 0 if x == 0 else 255, "1")
        # Create a new image with the same size as each frame
        frame_with_background = Image.new("RGBA", image.size, (0, 0, 0, 255))
        # Paste the frame onto the black background
        frame_with_background.paste(frame, (0, 0), alpha)
        # Append the frame with the black background to the list of frames
        frames.append(frame_with_background)

    try:
        # Save the new gif with the black background
        frames[0].save(os.path.join(WIN_TMP, "corrected.gif"), save_all=True,
                       append_images=frames[1:], optimization=False)
        return os.path.join(WIN_TMP, "corrected.gif")
    except PIL.UnidentifiedImageError:
        return file_url


def process_gif(image, file_url) -> Tuple[bool, Union[str, None], bool, str]:
    """
    Processes gif to static image or mp4
    (If the gif has 1 frame it will be converted to a png and transparency removed,
     if it has duration of <5s it will loop over the gif to reach the target of >=5s and convert to mp4,
     if it's already >=5s it will be converted directly)
    :returns: success, media_url, and local (if media_url is local path)
    """
    if not image.is_animated:  # gif with 1 frame -> png
        image.seek(1)  # go to 1st frame
        # save the first frame to a png img
        image.save(os.path.join(WIN_TMP, 'verified.png'), **image.info)
        new_image = Image.open(os.path.join(WIN_TMP, 'verified.png'))
        return remove_transparency(new_image, os.path.join(WIN_TMP, 'verified.png'), ".png")
    else:  # animated gif -> mp4
        duration = find_gif_duration(image)
        file_url = remove_gif_transparency(image, file_url)
        if duration > 5:
            # FFMPEG command (without looping)
            command = f"{FFMPEG} -y -i {file_url} -c:v libx264 -movflags faststart -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" {os.path.join(WIN_TMP, 'verified.mp4')}"
            print_warning(
                f"CONVERTING GIF -> MP4 (This could take a little bit)")
            return_code = os.system(command)
            if return_code != 2:
                return True, os.path.join(WIN_TMP, 'verified.mp4'), True, ".mp4"
            else:
                return False, file_url, False, ".gif"
        else:
            # Calculate the number of times the GIF needs to be looped to reach the target duration
            n_loops = int((5 // duration) + 1)
            # FFMPEG command
            command = f"{FFMPEG} -y -stream_loop {n_loops} -i {file_url} -c:v libx264 -movflags faststart -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" {os.path.join(WIN_TMP, 'verified.mp4')}"
            print_warning(
                f"CONVERTING GIF --[{n_loops} loops]-> MP4 (This could take a little bit)")
            return_code = os.system(command)
            if return_code != 2:
                return True, os.path.join(WIN_TMP, 'verified.mp4'), True, ".mp4"
            else:
                return False, file_url, False, ".gif"


def process_svg(svg_url, local) -> Tuple[bool, Union[str, None], bool, str]:
    """
    Processes svg to png
    :returns: success, media_url, and local (if svg_url is local path)
    """
    svg_path = os.path.join(WIN_TMP, "conversion.svg")
    png_path = os.path.join(WIN_TMP, "verified-svg.png")
    if not local:
        path = urllib.request.urlopen(svg_url).read()
        with open(svg_path, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(path)

    # -w 1920 option will distort the image.  by just providing one dimension, aspect ratio is maintained
    command = f"{INKSCAPE} -z -e {png_path} -h 1080 {svg_path}"
    err = subprocess.run(command.split(" "), capture_output=True).stderr

    # deprecation warning gets printed to stderr unfortunately
    if b"Inkscape" not in err:  # TODO: this is bad and misses legit errors.
        return True, png_path, True, ".png"
    else:
        print_error(f"Unable to convert svg to png: {err}")
        return False, svg_url, False, ".svg"


def remove_transparency(image, file_url, extension) -> Tuple[bool, Union[str, None], bool, str]:
    """
    Removes transparent background from png to opt for a black background
    :returns: success, media_url, local (if svg_url is local path), and extension
    """

    # convert alpha channel colors back to their respective color without any transparency
    image = image.convert('RGBA')

    new_image = Image.new("RGBA", image.size, "BLACK")
    new_image.paste(image, (0, 0), image)

    try:
        new_image.save(os.path.join(WIN_TMP, 'corrected.png'), **image.info)
        return True, os.path.join(WIN_TMP, 'corrected.png'), True, ".png"
    except PIL.UnidentifiedImageError:
        return False, file_url, False, extension


def verify_image_integrity(file_url: str, mime: str, local: bool, extension: str) -> Tuple[
        bool, Union[str, None], bool, str]:
    """
    Verifies image media integrity (i.e. png, jpg, gif, etc.)
    :returns: success, media_url, local (if media_url is local path), and extension
    """
    valid_types = [
        "image/png",
        "image/jpeg",
        "image/svg+xml",
        "image/gif"
    ]

    # this function is only for image media integrity :)
    if mime not in valid_types:
        return True, file_url, local, extension

    # svg has separate processing because of vector graphics
    if mime != "image/svg+xml":
        try:  # test if input is image
            if local:
                im = Image.open(file_url)
            else:
                try:
                    path = io.BytesIO(urllib.request.urlopen(file_url).read())
                    im = Image.open(path)
                except (URLError, ValueError):
                    print_error("Bad URL")
                    return False, file_url, local, extension
        except PIL.UnidentifiedImageError:  # input is not image
            print_error("Bad path or not image.")
            return False, file_url, local, extension

    if mime == 'image/svg+xml':
        success, path, _, _ = process_svg(file_url, local)
        if success:
            try:
                image = Image.open(path)
                return remove_transparency(image, path, extension)
            except PIL.UnidentifiedImageError:
                print_error("Something went wrong")
                return False, file_url, local, extension
        else:
            return False, file_url, local, extension
    elif mime == 'image/png':
        return remove_transparency(im, file_url, extension)
    elif mime == 'image/gif':
        return process_gif(im, file_url)
    else:  # if image is not a gif
        try:
            if not is_ffmpeg_compatible(file_url):  # Check if not compatible
                # If not compatible re-save image
                im.save(os.path.join(WIN_TMP, "verified-ffmpeg.png"))
                # Check compatibility again
                if is_ffmpeg_compatible(os.path.join(WIN_TMP, "verified-ffmpeg.png")):
                    # File converted to compatible image format
                    return True, os.path.join(WIN_TMP, 'verified-ffmpeg.png'), True, ".png"
                else:
                    # File is corrupt
                    print_error("Image cannot be verified nor converted.")
                    return False, None, local, extension
            else:
                # file is already ffmpeg compatible
                return True, file_url, local, extension
        except Exception as e:
            # subprocess error, or pillow saving error; file could not be verified
            print_error(f'File could not be verified with mime: {mime}; {e}')
            return False, None, local, extension


####### PWD MODULE IS NOT SUPPORTED FOR WIN ARCHITECTURE #######
# def user_exists(username):
#     try:
#         pwd.getpwnam(username)
#         return True
#     except KeyError:
#         return False


def get_valid_hostname(computer_number=None):
    good_host = False
    while not good_host:
        if computer_number:
            computer_host = "tbl-h10-{}".format(computer_number)
        else:
            computer_host = input_styled(
                "Which computer? (e.g. 'tbl-h10-12', or '192.168.3.125' or [q]uit) ")

        if computer_host == 'q':
            print("Quitting this.")
            return None

        good_host = host_exists(computer_host)

        if computer_number and not good_host:  # this computer # doesn't exist or can't connect
            return None

        if good_host:
            return computer_host


def host_exists(hostname, verbose=True, use_fqdn=True):
    if use_fqdn:
        hostname_2 = get_fqdn(hostname)
    else:
        hostname_2 = hostname

    # ping once with 1 second wait/time out
    ping_cmd = ['ping', '-c 1', '-W 1', hostname_2]
    if verbose:
        print_warning(
            "Checking to see if {} is connected to the network.".format(hostname_2))

    compeleted = subprocess.run(ping_cmd)

    if compeleted.returncode != 0:  # not success
        # Try again without fqdn, just in case
        if use_fqdn:
            return host_exists(hostname, verbose=True, use_fqdn=False)

        if verbose:
            print_error(
                "{} was not found on the network.  Is there a typo? Is the computer on?".format(hostname))
        return False
    else:
        if verbose:
            print_success("{} found on the network.".format(hostname))
        return True


def get_fqdn(hostname):
    """ Appends the local domain "hackerspace.tbl" if it isn't already there """
    if LOCALDOMAIN not in hostname:
        hostname = f"{hostname}.{LOCALDOMAIN}"
    return hostname


def input_plus(prompt, default=None, validation_method=None):
    """ Gets styled user input with a defualt value and option to quit.  Returns 'q' if quitting.
    Validation_method is not yet implemented.
    """
    hints_str = "[q]uit"

    if default:
        hints_str += f" | [Enter] = {default}"

    prompt = prompt + " (" + hints_str + "): "
    response = input_styled(prompt).strip()
    if response == "":  # they just hit enter for default, or None
        return default
    elif response.lower() == "q":
        print("quitting...")
        return response.lower()
    else:
        return response


def confirm(prompt, yes_is_default=True):
    """Ask the use to confirm an action (the prompt) with y or n."""

    if yes_is_default:
        yn_prompt = " [y]/n "
    else:
        yn_prompt = " y/[n] "

    do_it = input_styled(prompt + yn_prompt, color=ByteStyle.Y_N)

    if yes_is_default:
        if do_it == "" or do_it[0].lower() != 'n':
            return True
        else:
            return False
    else:
        if do_it == "" or do_it[0].lower() != 'y':
            return False
        else:
            return True

# def get_admin_pw():
#     # ask for admin password
#     while True:
#         password = getpass("Enter admin password: ")
#         print("Give me a moment to check the password...")
#         completed_process = subprocess.run(
#             ["su", "hackerspace_admin", ">", "/dev/null"],
#             text=True,
#             input=password,
#             capture_output=False)
#         if completed_process.returncode == 0:
#             # it's good
#             return password
#         else:
#             # bad password
#             print_error("Incorrect Password. Try again.")
