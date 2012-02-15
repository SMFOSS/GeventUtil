from setuptools import setup
from setuptools import find_packages

requires = [
    "PasteDeploy",
    "gevent",
    "gservice",
    "path.py"
    ]

version = '0.1.1'

setup(name='GeventUtil',
      version=version,
      description="Some helper for working with gevent",
      long_description=open('README.rst').read(),
      classifiers=[], 
      keywords='gevent monkeypatch',
      author='whit',
      author_email='whit at surveymonkey.com',
      url='http://surveymonkey.github.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      [console_scripts]
      gex=geventutil.script:main
      
      [paste.server_factory]
      main=geventutil.servers:GeventServerFactory

      [paste.filter_app_factory]
      exiting=geventutil.servers:make_exiting
      """,
      )
