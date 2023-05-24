import os
import subprocess

DAEMONS = ["snomiotgui.service", "knxmonitor.service", "snomsyslog.service"]

def symlink_exists(link_path: str) -> str:
    if os.path.exists(link_path) and os.path.islink(link_path):
        return f"Symlink {link_path} exists and is not broken"
    return f"Symlink {link_path} does not exists or is broken"

def create_daemons_symlinks():
    working_directory = "/usr/local/snom_baos_777"
    destination = "/etc/systemd/system"

    for source_file in DAEMONS:
        source_path = f"{working_directory}/{source_file}"
        link_path = f"{destination}/{source_file}"

        try:
            os.symlink(source_path, link_path)
        except FileExistsError:
            os.remove(link_path)
            os.symlink(source_path, link_path)

        message = symlink_exists(link_path)
        print(message)

def start_daemons():
    command = f"systemctl start {' '.join(DAEMONS)}"
    print(f"Executing '{command}'")
    subprocess.run([command], shell=True, capture_output=True)

def daemons_are_running():
    for daemon in DAEMONS:
        command = f"systemctl show {daemon} --property SubState"
        print(f"Executing '{command}'")
        output = subprocess.check_output([command], shell=True, encoding="UTF-8").strip()
        print(": ".join([daemon, output]))

        assert output == "SubState=running", f"\n{daemon} is not running ({output})"


if __name__ == "__main__":
    create_daemons_symlinks()
    start_daemons()
    daemons_are_running()
