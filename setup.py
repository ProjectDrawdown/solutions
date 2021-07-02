import os
import fnmatch
from setuptools import setup, find_packages

EXTENSIONS = ['*.zip', '*.csv', '*.json', '*.xlsx', '*.xlsm']

def recursive_get_package_data():
  '''
    Recursively add the absolute filepath of data to package
    that has the extensions from the EXTENSIONS array.
  '''
  matches = []
  THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
  for ext in EXTENSIONS:
      for root, dirnames, filenames in os.walk(THIS_FILE_DIR):
          for filename in fnmatch.filter(filenames, ext):
              matches.append(os.path.join(os.path.relpath(root, THIS_FILE_DIR), 
                                          filename))
          for dirname in dirnames:
              for root, dirnames, filenames in os.walk(dirname):
                for filename in fnmatch.filter(filenames, ext):
                  matches.append(os.path.join(
                    os.path.relpath(root, os.path.join(THIS_FILE_DIR, dirname)), filename))

  return matches

def list_package_dependencies():
  '''
    return the list of dependencies as array of string
  '''
  with open('requirements.txt') as f:
      required = f.read().splitlines()

  return required

setup(
  name='drawdown-solutions',
  version='1.0',
  description='TODO: add short description',
  package_data = {
      '': recursive_get_package_data(),
  },
  packages=find_packages(
    # This can be removed once the rest of the project is cleaned up
    exclude = ['alembic', 'api', 'limbo', 'test'],
  ),
  install_requires=list_package_dependencies(),
  url='https://github.com/ProjectDrawdown/solutions',
  license='LICENSE',
  long_description=open('README.md').read(),
)
