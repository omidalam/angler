from setuptools import find_packages,setup

setup(name='angler',
      version='0.1.1',
      description='Package for fluorescent microscopy image analysis.',
      url='https://github.com/omidalam/angler',
      author='Omid Gholamalamdari',
      author_email='qolam@omidalam.com',
      license='BSD',
      packages=find_packages(),
      install_requires=[
          'scikit-image==0.15.*',
          'numpy',
          'scipy',
          'matplotlib',
          'python-bioformats',
          'reportlab',
          'PyPDF2'
      ],
      inculde_package_data=True,
      zip_safe=False)