from distutils.core import setup

setup(name='File Deduper',
    version='0.9',
    description='Scan for and index files, then present files with matching'
    'hashes, preselecting one to save.',
    author='Chris Speck',
    author_email='chris@chrisspeck.com',
    url='http://www.chrisspeck.com/',
    packages=['deduper'],
    scripts=['scripts/deduper'],
    install_requires=['pythondialog',
    'sqlalchemy',
    'pillow']
      )
