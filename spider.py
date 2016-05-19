import os


class Spider(object):
    def __init__(self, root):
        self.root_path = root
        self.outputs=[]
    
    def crawl(self):
        for root, subfolders, files in os.walk(self.root_path):
            for file_name in files:
                if file_name == '__pub.lish':
                    self.outputs.append(root)
        return self.outputs
