# -*- mode: python -*-
import os
import re

cwd = os.getcwd()

tools_xdoc_path = os.path.join(cwd,'..','tools_xdoc')

sys.path.insert(0,tools_xdoc_path)

a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(HOMEPATH,'support/useUnicode.py'), 'scripts/xpd', '../tools_xdoc/xdoc/xsphinx/conf.py','../tools_xdoc/xdoc/xsphinx/breathe/breathe/__init__.py','../infr_docs/xmossphinx/xmosconf.py'],

             pathex=[cwd,
                     os.path.join(cwd,'xpd'),
                     os.path.join(cwd,'..','tools_python_hashlib','install','lib','python'),
                     os.path.join(cwd,'..','tools_python_hashlib','install','lib64','python'),
                     tools_xdoc_path,
                     os.path.join(tools_xdoc_path,'xdoc'),
                     os.path.join(tools_xdoc_path,'xdoc','xsphinx'),
                     os.path.join(tools_xdoc_path,'xdoc','xsphinx','breathe'),
                     os.path.abspath(os.path.join(cwd,'..','infr_docs')),
                     os.path.abspath(os.path.join(cwd,'..','infr_docs','xmossphinx','builders'))                     ],
             hiddenimports=['sphinx.builders.text','breathe','breathe.builder','breathe.finder',
                            'breathe.parser','breathe.parser.doxygen','breathe.parser.doxygen.index','breathe.parser.doxygen.compound',
                            'breathe.parser.doxygen.compoundsuper','xmosconf'])


def get_files(src, dst):
    def walk(path, prefix):
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path,f)):
                for x in walk(os.path.join(path,f),os.path.join(prefix,f)):
                    yield x
            else:
                yield os.path.join(prefix, f)

    import re
    files = []
    for path in walk(src,''):
        if not re.match('.*pyc$',path):
            files.append(path)

    return [(os.path.normpath(os.path.join(dst,p)),os.path.abspath(os.path.join(src,p)),'DATA') for p in files]

data_files = ['xsphinx/Doxyfile','xsphinx/conf.py']

xmosroot = os.environ['XMOS_ROOT']

data_files_toc = [(p,os.path.join(xmosroot,'tools_xdoc','xdoc',p),'DATA') for p in data_files] + \
                 get_files('../tools_xdoc/xdoc/xsphinx/themes','xsphinx/themes') + \
                 get_files(os.path.join(xmosroot,'infr_docs','base'),'texinputs') + \
                 get_files(os.path.join(xmosroot,'infr_docs/xmossphinx/themes'),'infr_docs/xmossphinx/themes') + \
                 get_files('../tools_xdoc/xdoc/texinput','texinputs') + \
                 get_files('../tools_xdoc/texinputs','texinputs')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('dist', 'xpd.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               data_files_toc,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'xpd'))

