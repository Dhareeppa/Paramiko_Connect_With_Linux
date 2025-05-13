import paramiko

ssh_client = paramiko.SSHClient()
current_directory = "/home/kali"
user = ""
hostName = ""


def SSH_Connect(Host, Port, userName, Password):
    global ssh_client, user, hostName
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=Host,
                           port=Port,
                           username=userName,
                           password=Password,
                           look_for_keys=False, allow_agent=False)
        user = userName
        stdin, stdout, stderr = ssh_client.exec_command("hostname")
        hostName = stdout.read().decode().strip()
        return True, f"Connected to {hostName}"
    except Exception as Err:
        return False, f"Error Occurred: {Err}"


def ExecutingCommands(command_argument):
    global current_directory, user, hostName, ssh_client
    if command_argument == "exit":
        ssh_client.close()
        return True, "Connection closed."

    if command_argument.startswith("cd"):
        target_directory = command_argument[3:].strip()
        if target_directory == "":
            current_directory = "/home/kali"
        elif target_directory == "..":
            current_directory = "/".join(current_directory.split("/")[:-1])
        else:
            new_directory = f"{current_directory}/{target_directory}"
            cd_stdin, cd_stdout, cd_stderr = ssh_client.exec_command(f"cd {new_directory} && pwd")
            error = cd_stderr.read().decode().strip()
            if error:
                return False, f"Error: {error}"
            else:
                current_directory = cd_stdout.read().decode().strip()
                return True, ""

    command = f"export TERM=xterm; cd {current_directory} && {command_argument}"
    EX_stdin, EX_stdout, EX_stderr = ssh_client.exec_command(command)
    output = EX_stdout.read().decode()
    error = EX_stderr.read().decode()
    if output:
        return True, output
    else:
        return False, error


def get_prompt():
    global current_directory, user, hostName
    prompt = f"┌──({user}㉿{hostName})-[{current_directory}]\n└─$ "
    return prompt
