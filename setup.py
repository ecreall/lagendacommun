import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'Babel',
    'icalendar',
    'Paste',
    'Pillow',
    'ecreall_dace',
    'ecreall_daceui',
    'deform',
    'dogpile.cache',
    'elasticsearch',
    'gunicorn',
    'plone.event',
    'ecreall_pontus',
    'pyramid',
    'pyramid_authstack',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_layout',
    'pyramid_mailer',
    'pyramid_robot',
    'pyramid_tm',
    'velruse',
    'robotframework-debuglibrary',
    'substanced',
    'waitress',
    'xlrd',
    'html_diff_wrapper',
    'Genshi',
    'deform_treepy',
    'url_redirector',
    'python-arango',
    'graphql-wsgi',
    'graphene',
    ]

setup(name='lac',
      version='0.0',
      description='lac',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons substanced',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="lac",
      message_extractors={
          'lac': [
              ('**.py', 'python', None), # babel extractor supports plurals
              ('**.pt', 'chameleon', None),
          ],
      },
      extras_require = dict(
          test=['pyramid_robot',
                'robotframework-debuglibrary',
                'robotframework-selenium2screenshots'],
      ),
      entry_points="""\
      [paste.app_factory]
      main = lac:main
      """,
      )

