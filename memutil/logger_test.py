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

"""Tests for `logger` module."""

import csv
import json
import unittest
import tempfile

from memutil import logger


class BuddyInfoLoggerTest(unittest.TestCase):
  """Tests for `BuddyInfoLogger` class."""

  def setUp(self) -> None:
    self._label = 'test-buddy-info-logger'

  def test_read_buddy_info(self):
    logger_ = logger.BuddyInfoLogger('dir', self._label)
    data = logger_.read_buddy_info()
    self.assertGreater(len(data.numa_nodes), 0)

  def test_snapshot(self):
    with tempfile.TemporaryDirectory() as output_dir:
      with logger.BuddyInfoLogger(output_dir, self._label) as logger_:
        logger_.snapshot()
        output_path = logger_.output_path

      with open(output_path) as fp:
        json_objects = []
        for line in fp:
          json_objects.append(json.loads(line))

      self.assertEqual(len(json_objects), 1)


class PsUtilLoggerTest(unittest.TestCase):
  """Tests for `PsUtilLogger` class."""

  def setUp(self) -> None:
    self._label = 'test-ps-util-logger'

  def test_snapshot(self):
    with tempfile.TemporaryDirectory() as output_dir:
      with logger.PsUtilLogger(output_dir, label=self._label) as logger_:
        logger_.snapshot()
        self.assertEqual(logger_.snapshot_count, 1)
        output_path = logger_.output_path

      with open(output_path) as fp:
        reader = csv.reader(fp)
        header = next(reader)
        self.assertCountEqual(logger.PsUtilLogger._CSV_HEADER, header)
        rows = [row for row in reader]
        self.assertEqual(1, len(rows))

  def test_output_filename_ok(self):
    logger_ = logger.PsUtilLogger('dir', label='label')
    self.assertIn(logger_._OUTPUT_PREFIX, str(logger_.output_path))


if __name__ == '__main__':
  unittest.main()
