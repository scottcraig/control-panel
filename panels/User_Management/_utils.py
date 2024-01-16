from panels._utils import utils
# from panels.TVs._utils import get_display_name

def get_display_name_from_username(username):
    """ Parse 'Firstname Lastname' from username 'firstname.lastname'"""
    if "." in username:
        fullname = username.replace(".", " ").title()
    else:
        return None

def get_and_confirm_user(username=None):
    """ Ask for a username (if not provided) and checks if it exists. If it does, returns a tuple of
    (fullname, username), if it does not, will return None, username
    """
    if not username:
        username = utils.input_styled("Enter username: ")

    fullname = get_display_name_from_username(username)

    if fullname is None:
        utils.print_warning("Unrecognized username expected format 'firstname.lastname' -- {}.".format(username))
        return None, username
    else:
        utils.print_success("Parsing name from username {}: {}.".format(username, fullname))
        is_correct_user = utils.confirm("Is this the correct student?", yes_is_default=False)

        if is_correct_user:
            return fullname, username
        else:
            return None, username