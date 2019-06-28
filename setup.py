from setuptools import find_packages,setup

setup(name='angler',
      version='0.1.0',
      description='Package for fluorescent microscopy image analysis.',
      url='https://github.com/omidalam/angler',
      author='Omid Gholamalamdari',
      author_email='qolam@omidalam.com',
      license='BSD',
      packages=find_packages(),
      install_requires=[
          'scikit-image',
          'numpy',
          'scipy',
          'matplotlib',
          'pyimagej',
          'reportlab'
      ],
      inculde_package_data=True,
      zip_safe=False)