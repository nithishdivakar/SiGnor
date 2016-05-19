import os

def copy(source,destination):
    command = "rsync -avrz {src} {des}".format(src=source,des=destination)
    os.system(command)
    return True
