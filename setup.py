from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='GeventUtil',
      version=version,
      description="Some helper for working with gevent",
      long_description="""
      """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='gevent monkeypatch',
      author='whit',
      author_email='whit at surveymonkey.com',
      url='http://surveymonkey.github.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["gevent"],
      entry_points="""
      [console_scripts]
      gmp=geventutil.script:main
      
      [paste.server_factory]
      gevent=monkeylib.servers:gevent_factory
      """,
      )
