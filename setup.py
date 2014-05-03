import os
from setuptools import setup


def find_packages(dir_):
    packages = []
    for _dir, subdirectories, files in os.walk(os.path.join(dir_, 'rfk')):
        if '__init__.py' in files:
            lib, fragment = _dir.split(os.sep, 1)
            packages.append(fragment.replace(os.sep, '.'))
    return packages

setup(
    name='PyRfK',
    version='0.1',
    long_description=__doc__,
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    include_package_data=True,
    zip_safe=False,
    entry_points={'console_scripts': ['rfk-werkzeug = rfk.app:main',
                                      'rfk-collectstats = rfk.collectstats:main',
                                      'rfk-geoipdbupdate = rfk.geoipdbupdate:main',
                                      'rfk-liquidsoaphandler = rfk.liquidsoaphandler:main',
                                      'rfk-liquidsoap = rfk.liquidsoapdaemon:main',
                                      'rfk-userstats = rfk.userstats:main',
                                      'rfk-setup = rfk.setup:main']},
    install_requires=['Flask', 'Flask-Login', 'Flask-Babel',
                      'wtforms',
                      'pytz',
                      'passlib',
                      'bcrypt',
                      'pycountry',
                      'geoip2',
                      'postmarkup',
                      'sqlalchemy',
                      'parsedatetime',
                      'icalendar',
                      'humanize',
                      'netaddr',
                      'chardet']
)
