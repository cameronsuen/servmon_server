from setuptools import setup

setup(
    name='servmon_server',
    packages=['servmon_server'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-socketio',
        'eventlet',
        'apscheduler',
        'flask-cors',
        'gunicorn'
    ]
)
