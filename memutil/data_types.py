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

"""Common data types."""

from typing import Sequence

import dataclasses
import dataclasses_json

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class Zone:
  """Zone from /proc/buddyinfo.

  Attributes:
    free_fragments: Free memory segments by order.
  """
  zone_type: str
  free_fragments: Sequence[int]


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class NumaNode:
  """NUMA node from /proc/buddyinfo.

  Attributes:
    zones: Memory zones per memory node.
  """
  node_index: int
  zones: Sequence[Zone]


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class BuddyInfoData:
  """Structured contents of `/proc/buddyinfo` pseudo file.

  Attributes:
    timestamp: Timestamp in seconds from epoch.
    numa_nodes: NUMA nodes.
  """
  timestamp: int
  numa_nodes: Sequence[NumaNode]


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class MemoryFragmentation:
  """Memory fragmentation data for a particular NUMA node/zone.

  Args:
    timestamp: Timestamp in seconds from epoch.
    node_index: NUMA node index.
    zone_type: Zone type (e.g. DMA, Normal, etc.).
    percentage: Memory fragmentation percentage value in [0, 1].
  """
  timestamp: int
  node_index: int
  zone_type: str
  percentage: float

