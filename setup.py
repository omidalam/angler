from setuptools import setup

setup(name='angler',
      version='0.1',
      description='Package for fluorescent microscopy image analysis.',
      url='https://github.com/omidalam/angler',
      author='Omid Gholamalamdari',
      author_email='qolam@omidalam.com',
      license='BSD',
      packages=['angler'],
      install_requires=[
          'skimage',
          'numpy',
          'scipy',
          'matplotlib'
      ]
      zip_safe=False)