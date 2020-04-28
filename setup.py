from setuptools import setup, find_packages
import os

version = "3.1.1.dev0"

setup(
    name="recensio.imports",
    version=version,
    description="Import tools for recensio",
    long_description=open("README.txt").read() + "\n" + open("CHANGES.txt").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Framework :: Plone", "Programming Language :: Python",],
    keywords="",
    author="SYSLAB.COM",
    author_email="info@syslab.com",
    url="http://svn.plone.org/svn/collective/",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["recensio"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Products.CMFPlone",
        "zc.testbrowser",
        "pyPdf",
        "plone.resource",
        # -*- Extra requirements: -*-
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      triggerImport = recensio.imports.tools:triggerPloneImportFromRecensio

      [z3c.autoinclude.plugin]
      target = plone
      """,
)
