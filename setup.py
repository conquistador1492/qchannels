from setuptools import setup, find_packages

setup(name='qchannels',
      version='0.1',
      description='More comfortable interface for IBM Quantum Experience',
      author='Alexey Pakhomchik',
      author_email='aleksey.pakhomchik@gmail.com',
      license='',  # TODO
      packages=find_packages(exclude=['test*']),
      install_requires=[
          'qiskit==0.8.0',
          'jsonschema>=2.6.0',
          'psutil>=5.4.7',
          'nose'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
