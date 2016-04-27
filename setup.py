from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='smartframe',
      version=version,
      description="smarter dataframe for pandas like spss",
      long_description="""\
smarter dataframe for pandas like spss""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='dataframe pandas spss',
      author='xxxspy',
      author_email='xxxspy@126.com',
      url='mlln.cn',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
