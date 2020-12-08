# Extract sql commands from init sql. Assumes that no commands before DROP and no comments in between commands.
def extract_init_sql():
    cmd_list = []
    with open("C:\\Users\\ASUS\\Downloads\\databaseCreationScript.sql", "r") as file:
        data = file.read()
        data = data[data.find('DROP'):]
        cmd_list = data.replace("\n", " ").split(";")
        cmd_list = cmd_list[:-1]
        cmd_list = [cmd + ";" for cmd in cmd_list]

    return cmd_list