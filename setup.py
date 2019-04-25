import os

from setuptools import find_packages
from setuptools import setup


repo_url = 'https://github.com/macisamuele/fog_director_simulator'


def read(file_path):
    with open(file_path) as fh:
        return fh.read()


# Small hack to read the content of __init__.py without importing the whole modules
about = {}  # type: ignore
exec(read(os.path.join('fog_director_simulator', '__init__.py')), about)

setup(
    name='fog-director-simulator',
    version=about['__version__'],
    license='MIT license',
    description='',  # TODO
    long_description='{}\n{}'.format(
        read('README.rst'),
        read('CHANGELOG.rst')
    ),
    author='Alessandro Pagiaro',
    author_email='alessandropagiaro@gmail.com',
    url=repo_url,
    packages=find_packages(exclude=('test*', )),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: PyPy', # TODO: maybe in the future
    ],
    project_urls={
        'Changelog': '{}/blob/master/CHANGELOG.rst'.format(repo_url),
        'Issue Tracker': '{}/issues'.format(repo_url),
    },
    keywords=[],  # TODO
    python_requires='>=3.6',
    install_requires=[
        'sqlalchemy[mysql]',
    ],
    extras_require={
        ':python_version=="3.6"': ['typing_extensions'],
    },
    entry_points={
        'console_scripts': [
            # 'fog-director-simulator = fog_director_simulator.cli:main',
        ]
    },
)
