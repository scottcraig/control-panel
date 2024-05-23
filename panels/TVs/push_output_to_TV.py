import inquirer


def push_output_to_TV():
    

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
    hostname = inquirer.prompt(tv_list)["tv"]

    print(hostname)