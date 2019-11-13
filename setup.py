from setuptools import setup

setup(
    name='eglantine-skill',
    version='1.0',
    packages=[ 'musiccast', 'samsungtv', 'eglantinews'],
    install_requires = [
        'click==7.0',
        'flask===1.0.2',
        'flask-restful===0.3.6',
        'requests===2.22.0',
        'wakeonlan===1.1.6',
        'websockets===6.0',
        'kodi-json===1.0.0'
    ],
    url='',
    license='',
    author='pterrano',
    author_email='',
    description=''
)
