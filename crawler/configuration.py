from json import load

def read_config(sitename):
    with open("configs/" + sitename + ".json", "r") as f:
        return load(f)

def get_skip_xpaths(sitename):
    config = read_config(sitename)
    return config["skip_xpath"]
