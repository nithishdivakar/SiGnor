from jinja2 import Template,Environment, FileSystemLoader
from os import listdir
from os.path import isfile, join
import os
from shutil import copy as copy_file
import shutil
import tempfile
from distutils.dir_util import copy_tree
from tinydb import TinyDB,Query,where
import hashlib



class DB(object):
    def __init__(self):
        if os.path.exists('db.json'):
            os.remove("db.json")
        self.db = TinyDB("db.json",indent=2)

    def insert(self,table,key,value):
        table = self.db.table(table)
        R = value
        R['key'] = key
        table.insert(R)
    def get_all(self,table):
        return self.db.table(table).all()

_db = DB()

_slide_ext = 'svg'

_sty_content = open("Resources/post.sty","r").read()

_template = Environment(loader=FileSystemLoader("./"))

_make_file_cont='''
all: {in_file}.dvi
	@dvisvgm -v 0 --no-fonts --bbox=a6 --page=1- --output="slide-%p.{slide_ext}"     {in_file}.dvi

{in_file}.dvi:{in_file}.tex
	@latexmk -quiet -dvi {in_file}.tex
'''


def post_file_name_splitter(file_name):
    '''
        yyyy-mm-dd-title-sep-dashes.tex
    '''
    pieces = file_name.split("-")
    file_name_record={
        'year'     :pieces[0],
        'month'    :pieces[1],
        'day'      :pieces[2],
        'title'    :"-".join(pieces[3:]),
        'file_name':file_name,
    }
    return file_name_record

def handle_js():
    if os.path.exists('Site/js'):
        shutil.rmtree('Site/js')
    
    if os.path.exists('js'):
        shutil.copytree('js', 'Site/js')

def handle_css():
    if os.path.exists('Site/css'):
        shutil.rmtree('Site/css')

    if os.path.exists('css'):
        shutil.copytree('css', 'Site/css')

def post_discovery():
    for root, subfolders, files in os.walk('Posts'):
        for file_name in files:
            if file_name.endswith('.tex'):
                R = post_file_name_splitter(file_name)
                R['root_path']=root
                value = R
                key   = hashlib.sha224(str(R)).hexdigest()
                _db.insert("posts",key,value)

def post_compile():
    temp_dire = os.path.join(tempfile.gettempdir(), 'BLA')
    if os.path.exists(temp_dire):
        shutil.rmtree(temp_dire)
    copy_tree("Posts", os.path.join(temp_dire,"Posts"))
    owd = os.getcwd()
    os.chdir(temp_dire)
    op_list = []
    for post_reco in _db.get_all('posts'):
        slides = post_gen_one(post_reco)
        op_list.append((post_reco['root_path'],post_reco['title'][:-4],slides))

    os.chdir(owd)
    for root_fldr,post_fldr,slides in op_list:
        try:
            os.makedirs(os.path.join("Site",root_fldr))
        except:
            print '.'
        for slide in slides:
            shutil.copy(os.path.join(temp_dire,root_fldr,slide),
                os.path.join("Site",root_fldr,slide))
    
        P = _template.get_template('Templates/post.html')
        html_content = P.render(slides=sorted(slides))
        html_file = os.path.join("Site",root_fldr, 'index.html')
        open(html_file , "w").write(html_content)
    

def make_pages():
    posts=[]
    months=[ 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    for R in _db.get_all('posts'):
        posts.append({
            'title': R['title'][:-4].replace('-',' '),
            'url'  : os.path.join(R['root_path']),
            'year' : R['year'],
            'day'  : R['day'],
            'month': months[int(R['month'])-1],
        })
    for file_name in os.listdir('./'):
        if file_name.endswith('.html'):
            P = _template.get_template(file_name)
            html_content = P.render(posts=posts)
            html_file = os.path.join("Site", file_name)
            open(html_file , "w").write(html_content)

def post_gen_one(post_reco):
    owd = os.getcwd()
    os.chdir(post_reco['root_path'])


    make_file_cont = _make_file_cont.format(
        slide_ext = _slide_ext,
        in_file   = post_reco['file_name'][:-4]
    )
    open("Makefile","w").write(make_file_cont)
    open("post.sty","w").write(_sty_content)
    os.system("make")
    slides = [f for f in os.listdir('./') if f.endswith(_slide_ext) and f.startswith('slide')]
    os.chdir(owd)
    return slides



handle_js()
handle_css()
post_discovery()
post_compile()
make_pages()
