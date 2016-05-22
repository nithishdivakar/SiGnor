from jinja2 import Template, Environment, FileSystemLoader
import argparse
import distutils.dir_util 
import json
import json
import os
import shutil
import tempfile
import time

from compilers import HtmlCompiler,TexCompiler
from rsync import copy as rsync_copy
from spider import Spider


def log_it(Head="LOG", message=""):
	print "[{:>6}]: {}".format(Head,message)



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--src", nargs=1,  help="source directory",default="../nithishdivakar.github.io/src")
parser.add_argument("-o", "--out", nargs=1,  help="output directory",default="../nithishdivakar.github.io")
args = parser.parse_args()


args.out = args.out[0] if type(args.out)==list else args.out
args.src = args.src[0] if type(args.src)==list else args.src

out_dir = os.path.abspath(args.out)
src_dir = os.path.abspath(args.src)
#print os.path.abspath(args.src)
log_it("OUT DIR",out_dir)
log_it("SRC DIR",src_dir)

_template = Environment(loader=FileSystemLoader(os.path.abspath(src_dir)))


Templates={
    'html':_template.get_template('Templates/post.html'),
    'tex' :_template.get_template('Templates/post.html'),
}

Compilers={
    'html':HtmlCompiler(Templates['html']),
    'tex' :TexCompiler (Templates['tex']),
}

temp_dire = os.path.join('TMP') 
temp_dire = os.path.abspath(temp_dire)
'''
Creating workspacein tmp directory of os is 
creating many probs in osx. tmp directory change from /var
to ./private etc 
'''

log_it("TEMP DIR",temp_dire)

if os.path.exists(temp_dire):
    shutil.rmtree(temp_dire)
distutils.dir_util.copy_tree(src_dir,temp_dire)
owd = os.getcwd()

log_it("LOG","Crawling started")
spider = Spider(temp_dire)
log_it("LOG","Crawling done")
# spider.crawl()

log_it("LOG","Compileing pages started")
posts_data=[]
for post_folder in spider.crawl():
    config = json.load(open(os.path.join(post_folder,"__pub.lish")))
    t_date = time.strptime(config['date'],"%Y-%m-%d")
    posts_data.append({
        'title': config['name'].replace('-', ' '),
        'url'  : post_folder[len(temp_dire)+1:],
        'year' : time.strftime("%Y",t_date),
        'day'  : time.strftime("%d",t_date),
        'month': time.strftime("%b",t_date),
        'date' : t_date
    })
    compiler = Compilers[config['type']]
    owd = os.getcwd()
    os.chdir(post_folder)
    compiler.compile(config['file'])
    os.chdir(owd)

import operator
posts_data.sort(key = operator.itemgetter('date'),reverse=True)

log_it("LOG","Compileing pages done")

def smart_file_copy(src,dest):
    try:
        os.makedirs(os.path.dirname(dest))
    except:
        print '.'
    print "COPY:"
    print "FROM: "+src
    print "TO  : "+dest
    #shutil.copy(src,dest)
    rsync_copy(src,dest)
    return True


log_it("LOG","Copying thing into place")

for _,compiler in Compilers.iteritems():
    for f in compiler.get_output_files():
        smart_file_copy(f,os.path.join(out_dir,f[len(temp_dire)+1:]))

log_it("LOG","Copying thing into place : done")

configs = json.load(open(os.path.join(src_dir,"config.json")))
for static_dir in configs["static_dirs"]:
    distutils.dir_util.copy_tree(os.path.join(src_dir,static_dir),os.path.join(out_dir,static_dir))


for static_file in configs["static_files"]:
    smart_file_copy(os.path.join(src_dir,static_file),os.path.join(out_dir,static_file))



for active_file in configs["to_render"]:
    P = _template.get_template(active_file)
    html_content = P.render(posts=posts_data)
    html_file = os.path.join(out_dir, active_file)
    open(html_file, 'w').write(html_content)


shutil.rmtree(temp_dire)
