from setuptools import setup

setup(name='FileDeduper',
    version='0.9',
    description='Scan for and index files, then present files with matching'
    'hashes, preselecting one to save.',
    author='Chris Speck',
    author_email='chris@chrisspeck.com',
    url='http://www.chrisspeck.com/',
    packages=['deduper'],
    scripts=['scripts/deduper'],
    install_requires=['pythondialog', 'sqlalchemy', 'pillow'],
    extras_require={
    'tests': ['pytest', 'fudge', 'flake8']
    }
      )
