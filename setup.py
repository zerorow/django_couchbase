#!/usr/bin/env python

from setuptools import setup

setup(
      name="django-couchbase",
      version= '0.0.10',
      description="couchbase client for django memcache",
      long_description=open("README").read(),
      author="MaxiL",
      author_email="maxil@interserv.com.tw",
      maintainer="MaxiL",
      maintainer_email="maxil@interserv.com.tw",
      url="",
      download_url="",
      packages=["django_couchbase"],
      install_requires=[
      	'couchbase',
      ],
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ])

