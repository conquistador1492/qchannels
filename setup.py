from setuptools import setup, find_packages

setup(name='qchannels',
      version='0.1',
      description='More comfortable interface for IBM Quantum Experience',
      author='Alexey Pakhomchik',
      author_email='aleksey.pakhomchik@gmail.com',
      license='',  # TODO
      packages=find_packages(exclude=['test*']),
      install_requires=[
          'psutil>=5.4.7',
          'qiskit==0.11.1',
          'nose',
          'sympy'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
