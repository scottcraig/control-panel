import os
import inquirer
from .._utils import utils, pi
from .._utils.ssh import SSH
from ..User_Management import _utils as user_utils
from .add_new_media import add_new_media, refresh_slideshow




def make_new_title():

    print("\n ******** \n For this to work, make sure you have Ubuntu fonts installed on the computer, available through Google Fonts: https://fonts.google.com/specimen/Ubuntu \n ********\n")
    print("\nInkscape also needs to be installed. ********\n")

    print("\nThe file will be placed in the output folder.\n")

    username = utils.input_plus("Enter username for filename (firstname.lastname): ")
    if username == "q":
        return
    fullname = utils.input_plus("Enter the name to appear in the title card: ")
    if fullname == "q":
        return
    grad_year = utils.input_plus("Grad Year: ")
    if grad_year == "q":
        return

    subject_list = [
        inquirer.List('subject',
                      message="What subject is the student in?",
                      choices=['Digital Art', 'Digital Photography', '3D Modelling & Animation', 'Custom subject:'],
                      ),
    ]

    choose_subject = inquirer.prompt(subject_list)["subject"]

    # gets user to input a custom subject if they so choose
    if choose_subject == "Custom subject:":
        custom_subject = utils.input_styled("What is the subject? \n")
        choose_subject = custom_subject

    filename = username + ".a.title"
    template = "_template.svg"
    source_file = os.path.join("panels", "TVs", template)
    temp_filepath_svg = os.path.join(output_dir, f"{filename}.svg")
    filename_png = f"{filename}.png"
    out_filepath_png = os.path.join(utils.OUTPUT_DIR, filename_png)

    # creates copy of template with the filename it will use
    os.system("copy {} {}".format(source_file, temp_filepath_svg))

    # open the file and replace templated sections
    try:
        # Open the file in read mode
        with open(temp_filepath_svg, 'r') as file:
            # Read the content of the file
            content = file.read()

        content = content.replace('FIRSTNAME LASTNAME', fullname)
        content = content.replace('YYYY', grad_year)
        content = content.replace('SUBJECT', choose_subject.replace('&', '&amp;'))
        
        # Open the file in write mode to save the changes
        with open(temp_filepath_svg, 'w') as file:
            # Write the updated content back to the file
            file.write(content)

    except FileNotFoundError:
        print(f"Error: File not found at {temp_filepath_svg}")
     

    # # writes the student information into the copy of the svg template
    # os.system(f'echo.|set /p="FIRSTNAME LASTNAME={fullname}" > temp.txt && findstr /v /i "FIRSTNAME LASTNAME" {fullname} >> temp.txt && move /y temp.txt {temp_filepath_svg}')
    # ##(Linux Leftovers)# os.system('sed -i -e "s/FIRSTNAME LASTNAME/{}/g" {}'.format(fullname, temp_filepath_svg))

    # os.system(f'echo.|set /p="YYYY={grad_year}" > temp.txt && findstr /v /i "YYYY" {grad_year} >> temp.txt && move /y temp.txt {temp_filepath_svg}')
    # ##(Linux Leftovers)# os.system('sed -i -e "s/FIRSTNAME LASTNAME/{}/g" {}'.format(fullname, temp_filepath_svg))

    # os.system('echo.|set /p="SUBJECT={}" > temp.txt && findstr /v /i "SUBJECT" {} >> temp.txt && move /y temp.txt {}'.format(choose_subject.replace('&', '\&amp;'), temp_filepath_svg))
    # ##(Linux Leftovers)# os.system('sed -i -e "s/YYYY/{}/g" {}'.format(grad_year, temp_filepath_svg))

    # # need to escape the ampersand character in "3D Modelling & Animation"
    # os.system('sed -i -e "s/SUBJECT/{}/g" {}'.format(choose_subject.replace('&', '\&amp;'), temp_filepath_svg))

    # creates a png image from the svg
    # inkscape_command = f'{utils.INKSCAPE} -z -e {temp_filepath_png} -w 1920 -h 1080 {temp_filepath_svg}'
    inkscape_command = f'{utils.INKSCAPE} --export-filename={out_filepath_png} -w 1920 -h 1080 {temp_filepath_svg}'
    os.system(inkscape_command)


    if not os.path.isfile(out_filepath_png):
        utils.print_error(f"The title image '{filename_png}' was not added. Maybe inkscape isn't installed?")