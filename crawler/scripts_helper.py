import os

def get_injected_scripts():
    return read_file("injected_scripts.js")

def get_events_accessor():
    return read_file("get_element_events.js")

def read_file(filename):
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", filename))
    with open(path, "r") as f:
        return f.read()

if __name__ == '__main__':
    print(get_injected_scripts())