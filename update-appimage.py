import requests
import json
import argparse
import glob
import os

# path to program folder
PROGRAM_PATH = "/home/ubuntu/Programs/"
PATH_OF_SCRIPT = "/media/ubuntu/igel/Projekte/scripts/update-appimage/"

# available modes for download
# redirect-https-download for linphone
# github for nextcloud

def save_template():
    template = {
        "name": "NAME",
        "url": "https://",
        "version": "",
        "mode": "redirect-https-download"
    }

    json_object = json.dumps(template, indent=4)

    with open("name-update-appimage.json", "w") as outfile:
        outfile.write(json_object)

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def redirect_https_download(config):
    response = requests.get(config["url"], allow_redirects=False)
    location = response.headers['location']

    download_appimage(config, location)   


def github_download(config):    
    response = requests.get(config["url"], allow_redirects=True)
    github_data = response.json()
    location = github_data["assets"][2]["browser_download_url"]

    download_appimage(config, location)

def download_appimage(config, location):
    name = config["name"]

    if config["version"] != location:
        print("updating " + name + " to version " + location)

        # download new file
        response = requests.get(location, allow_redirects=True, stream=True)

        filepath = PROGRAM_PATH + os.path.basename(location)
        with open(filepath, 'wb') as outfile:
            outfile.write(response.content)

        make_executable(filepath)

        # update symlink
        symlink_name = PROGRAM_PATH + name + ".AppImage"
        if os.path.exists(symlink_name):
            os.remove(symlink_name)
        os.symlink(filepath, symlink_name)        

        # set new version in config
        config["version"] = location
        json_object = json.dumps(config, indent=4)

        with open(PATH_OF_SCRIPT + name + "-update-appimage.json", "w") as outfile:
            outfile.write(json_object)
        
    else:
        # version is up to date
        print(name + " is up to date")

def update_all():

    for config_file in glob.glob(PATH_OF_SCRIPT + "*-update-appimage.json"):
        f = open(config_file)
        config = json.load(f)
        mode = config["mode"]        
        
        if mode == "redirect-https-download":
            redirect_https_download(config)

        elif mode == "github-download":
            github_download(config)
        


        f.close()


def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-c", "--create", action='store_true', help="create template")

    args = argParser.parse_args()

    if args.create:
        save_template()
    else:
        update_all()


if __name__ == "__main__":
   main()
