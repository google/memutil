# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python package setup script."""

from setuptools import setup, find_packages

setup(
    name='memutil',
    version='0.1',
    author='Carlos Ezequiel',
    author_email='cezequiel@google.com',
    packages=find_packages(include=['memutil']),
    install_requires=[
        'dataclasses-json==0.6.1',
        'psutil==5.9.5',
    ],
)
