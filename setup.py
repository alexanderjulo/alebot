"""
    alebot
    ----------------

    alebot is a super lean and highly modularized irc bot that lets you
    extend it in a python way, using classes and decorators. It supports
    both hooks and background tasks in an easy and fail-safe way.

    Links
    `````

    * `source code <https://github.com/alexex/alebot>`_
    * `docs <https://alebot.readthedocs.org/
"""
from setuptools import setup


setup(
    name='alebot',
    version='0.1',
    url='https://github.com/alexex/alebot',
    license='MIT',
    author='Alexander Jung-Loddenkemper',
    author_email='alexander@julo.ch',
    description='A super lean and highly modularized irc bot',
    long_description=__doc__,
    packages=['alebot', 'alebot.plugins'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'click'
    ],
    entry_points='''
        [console_scripts]
        alebot=alebot.cli:run
    '''
)
