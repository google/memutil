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

"""Evaluates memory fragmentation.

Implementation inspired by:
- https://github.com/bittorf/calculate-linux-memory-fragmentation
"""

from typing import Sequence

from memutil import data_types


def _compute_memory_fragmentation_percentage(zone: data_types.Zone):
  """Computes memory fragmentation percentage for a zone."""
  pages_list = []
  multiplier = 1
  for fragments in zone.free_fragments:
    pages_list.append(fragments * multiplier)
    multiplier *= 2

  pages_total = sum(pages_list)
  percent_free_total = 0
  running_pages_total = 0
  for pages in pages_list:
    residual_pages = pages_total - running_pages_total
    running_pages_total += pages
    percent_free = 100 - (residual_pages * 100) / pages_total
    percent_free_total += percent_free

  zone_percent_free = percent_free_total / len(pages_list)
  return zone_percent_free


def compute_memory_fragmentation_percentages(
    data: data_types.BuddyInfoData,
) -> Sequence[data_types.MemoryFragmentation]:
  """Computes memory fragmentation percentages for each node/zone."""
  output = []
  for node in data.numa_nodes:
    for zone in node.zones:
      percentage = _compute_memory_fragmentation_percentage(zone)
      output.append(data_types.MemoryFragmentation(
          timestamp=data.timestamp,
          node_index=node.node_index,
          zone_type=zone.zone_type,
          percentage=percentage))

  return output

