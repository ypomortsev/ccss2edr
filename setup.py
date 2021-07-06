try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='ccss2edr',
      version='0.0.2',
      description='CCSS to EDR converter',
      author='Yegor Pomortsev',
      author_email='yegor@pomortsev.com',
      url='http://pomortsev.com',
      packages=['ccss2edr'],
      entry_points={
          'console_scripts': [
              'ccss2edr = ccss2edr.ccss2edr:main',
              'dumpedr = ccss2edr.dumpedr:main'
          ]
      })
