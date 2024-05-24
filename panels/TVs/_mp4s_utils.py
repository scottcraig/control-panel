import paramiko
import inquirer

username = 'pi'
password = 'hackerberry'
domain = '.hackerspace.tbl'
media_dir = 'rs_media'

def choose_TV():
    tv_list = [
        inquirer.List('tv',
                      message="Which TV?",
                      choices=[("TV1 for original artwork, students A-L", "pi-tv1"),
                               ("TV2 for original artwork, students M-Z", "pi-tv2"),
                               ("TV3 for demonstration artwork or Skills Cananda", "pi-tv3"),
                               ("TV4 for hallway", "pi-tv4"),
                               ],
                      ),
    ]
    return inquirer.prompt(tv_list)["tv"]


def choose_files(tv):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add host keys (not secure for production)
    ssh.connect(hostname=tv + domain, username=username, password=password)
    sftp = ssh.open_sftp()
    file_list = sorted(sftp.listdir(media_dir))
    sftp.close()
    ssh.close()

    chosen = inquirer.prompt(
        [
            inquirer.Checkbox('chosen_files',
                    message="Which files? use spacebar to select. arrows to move. enter when done.",
                    choices=file_list,
                    ),
        ]   

    )

    return chosen['chosen_files']
    