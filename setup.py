#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines() or []

with open('README.md') as f:
    readme = f.read() or ''

version = ''
with open('amongus/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set!')

if version.endswith(('a', 'b', 'rc')):
    try:
        import subprocess

        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
    except Exception:
        pass

extra_requirements = {
    'docs': [
        'sphinx',
        'sphinxcontrib_trio'
    ]
}

setup(
    name='amongus',
    version=version,
    description='Asynchronous Python Among Us Client',
    author='Technofab',
    author_email='amongusio.git@technofab.de',
    url='https://gitlab.com/TECHNOFAB/amongusio',
    license='MIT',
    packages=['amongus'],
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require=extra_requirements,
    python_requires='>=3.6',
)
