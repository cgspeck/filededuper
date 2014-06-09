from distutils.core import setup

setup(name='Image File Deduper',
    version='0.7',
    description='Scan for and index files, then present files with matching'
    'hashes, preselecting one to save ',
    author='Chris Speck',
    author_email='chris@chrisspeck.com',
    url='http://www.chrisspeck.com/',
    packages=['imagededuper'],
    scripts=['scripts/imagededuper'],
    install_requires=['ipdb',
    'sqlalchemy',
    'pillow'],
    test_requires=['pytest', 'fudge'],
    test_suite=['test']
      )
