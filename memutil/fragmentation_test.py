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
"""Tests for fragmentation module."""

import time
import unittest

from memutil import data_types
from memutil import fragmentation


def _get_sample_buddy_info_data(timestamp: int) -> data_types.BuddyInfoData:
  return data_types.BuddyInfoData(
      timestamp=timestamp,
      numa_nodes=[
          data_types.NumaNode(
              node_index=0,
              zones=[
                  data_types.Zone(
                    zone_type='DMA',
                    free_fragments=[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2]),
                  data_types.Zone(
                    zone_type='DMA32',
                    free_fragments=[2276, 2354, 2313, 2467, 2193, 1962, 1605,
                                    1083, 491, 157, 159]),
                  data_types.Zone(
                    zone_type='Normal',
                    free_fragments=[272212, 416747, 380128, 291594, 201237,
                                    133952, 72185, 37780, 19157, 8814, 17597]),
              ]
          ),
          data_types.NumaNode(
              node_index=1,
              zones=[
                  data_types.Zone(
                    zone_type='Normal',
                    free_fragments=[437273, 438880, 516277, 395388, 241545,
                                    134083, 69199, 33740, 14747, 5564, 17340]),
              ]
          ),
      ]
  )


class ComputeMemoryFragmentationPercentagesTest(unittest.TestCase):
  """Tests for `compute_memory_fragmentation_percentages`."""

  def _assert_memory_fragmentation_almost_equal(
      self,
      e: data_types.MemoryFragmentation,
      o: data_types.MemoryFragmentation) -> None:
    self.assertAlmostEqual(e.percentage, o.percentage, places=2)
    self.assertEqual(e.node_index, o.node_index)
    self.assertEqual(e.zone_type, o.zone_type)
    self.assertEqual(e.timestamp, o.timestamp)

  def test_sample_data_ok(self):
    timestamp = int(time.time())
    expected = [
        data_types.MemoryFragmentation(timestamp=timestamp,
                        node_index=0,
                        zone_type='DMA',
                        percentage=3.305785123966942),
        data_types.MemoryFragmentation(timestamp=timestamp,
                            node_index=0,
                            zone_type='DMA32',
                            percentage=23.949837530562288),
        data_types.MemoryFragmentation(timestamp=timestamp,
                            node_index=0,
                            zone_type='Normal',
                            percentage=23.350382593393853),
        data_types.MemoryFragmentation(timestamp=timestamp,
                            node_index=1,
                            zone_type='Normal',
                            percentage=25.97416028057038)
    ]
    output = fragmentation.compute_memory_fragmentation_percentages(
        _get_sample_buddy_info_data(timestamp))
    for e, o in zip(expected, output):
      self._assert_memory_fragmentation_almost_equal(e, o)


if __name__ == '__main__':
  unittest.main()
