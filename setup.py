try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Simple Markdown parser',
    'author': 'Arnaud Chen-yen-su',
    'url': 'https://github.com/arnaudchenyensu/markdown-parser',
    'download_url': 'https://github.com/arnaudchenyensu/markdown-parser/archive/master.zip',
    'author_email': 'arnaud.chenyensu@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['markdown-parser'],
    'scripts': [],
    'name': 'markdown-parser'
}

setup(**config)
