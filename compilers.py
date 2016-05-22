import os

class Compiler(object):
    ''' abstract base class '''
    def __init__(self):
        self.outputs=[]

    def compile(self,file_name):
        pass

    def add_outputs(self,out_files):
        cwd = os.getcwd()
        if isinstance(out_files,list):
            self.outputs.extend([os.path.join(cwd,f) for f in out_files])
        else:
            self.outputs.append([os.path.join(cwd,f) for f in out_files])

    def get_output_files(self):
        return self.outputs


class TexCompiler(Compiler):
    def __init__(self,template):
        super(TexCompiler, self).__init__()
        self.template = template
        self ._makefile_cont = '''
all: {in_file}.dvi
	@dvisvgm -v 0 --no-fonts --bbox=a6 --page=1- --output="slide-%p.{slide_ext}" {in_file}.dvi

{in_file}.dvi:{in_file}.tex
	@latexmk -quiet -dvi {in_file}.tex
        '''
        self._slide_ext='svg'

    def compile(self,file_name):
        if file_name.endswith('.tex'):
            file_name = file_name[:-4]
        makefile = self._makefile_cont.format(
            slide_ext=self._slide_ext,
            in_file=file_name
        )
        open('Makefile', 'w').write(makefile)
        #open('post.sty', 'w').write(_sty_content)
        os.system('make')
        '''
        slides = [f for f in os.listdir('./') if f.endswith(self._slide_ext) and f.startswith('slide')]
        self.add_outputs(slides)
        html = self.template.render(slides=sorted(slides))
        open("index.html",'w').write(html)
        self.add_outputs(["index.html"])
        return True
        '''
        slides = [f for f in os.listdir('./') if f.endswith(self._slide_ext) and f.startswith('slide')]
        from bs4 import BeautifulSoup as BS
        content = [BS(open(f),'html.parser').svg for f in slides]
        #self.add_outputs(slides)
        html = self.template.render(slides=content)
        open("index.html",'w').write(html)
        self.add_outputs(["index.html"])
        return True


class HtmlCompiler(Compiler):
    def __init__(self,template):
        super(HtmlCompiler, self).__init__()
        self.template = template
        
    def compile(self,file_name):
        content = open(file_name,'r').read()
        html = self.template.render(content=content)
        open("index.html",'w').write(html)
        self.add_outputs(["index.html"])
        return True
        
