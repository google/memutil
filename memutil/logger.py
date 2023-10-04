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

"""Tools for logging physical memory metrics."""

import abc
import csv
from datetime import datetime
import pathlib
import re
import time
from typing import Dict, Optional, Sequence

import psutil

from memutil import data_types


NumaNode = data_types.NumaNode
Zone = data_types.Zone
BuddyInfoData = data_types.BuddyInfoData


def _get_timestring() -> str:
  return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


class BaseLogger(abc.ABC):
  """Base class for memory loggers."""

  @abc.abstractmethod
  def __init__(self, output_dir: str, label: Optional[str] = None) -> None:
    """Initialize.

    Args:
        output_dir: Output directory to store log file.
        label: Label string to include in the log file name.
    """

  @abc.abstractmethod
  def snapshot() -> None:
    """Takes a snapshot of memory allocation."""

  @abc.abstractmethod
  def __enter__(self):
    """Context manager `__enter__` method."""

  @abc.abstractmethod
  def __exit__(self, exc_type, exc_value, exc_tb):
    """Context manager `__exit__` method."""


class BuddyInfoLogger(BaseLogger):
  """Logger for /proc/buddyinfo in Linux.

  Used for checking memory fragmentation.
  """

  _BUDDY_INFO_PSEUDO_FILE = '/proc/buddyinfo'
  _BUDDY_INFO_LINE_REGEX = re.compile(
      r'Node\s+(?P<numa_node>\d+).*zone\s+(?P<zone>\w+)\s+(?P<nr_free>.*)')
  _OUTPUT_SUFFIX = '.jsonl'
  _OUTPUT_PREFIX = 'proc-buddyinfo-log'

  def __init__(self, output_dir: str, label: Optional[str] = None) -> None:
    """Initialize."""
    output_basename = self._OUTPUT_PREFIX
    if label:
      output_basename += f'-{label}'
    timestring = _get_timestring()
    output_basename += f'-{timestring}'
    self._output_path = (pathlib.Path(output_dir) /
                         output_basename).with_suffix(self._OUTPUT_SUFFIX)
    self._start_time = 0
    self._output_file_object = None
    self._snapshot_count = 0

  def _parse_line(self, line: str) -> Dict[str, str]:
    line = line.strip()
    tokens = re.match(self._BUDDY_INFO_LINE_REGEX, line).groupdict()
    return tokens

  @staticmethod
  def _parse_tokens(
      tokens: Dict[str, str],
      numa_nodes: Dict[int, NumaNode],
  ) -> None:
    numa_node_index = tokens['numa_node']
    zone_type = tokens['zone']
    free_fragments = [int(x) for x in tokens["nr_free"].split()]
    zone = Zone(zone_type=zone_type, free_fragments=free_fragments)
    if numa_node_index in numa_nodes:
      numa_node = numa_nodes[numa_node_index]
      numa_node.zones.append(zone)
    else:
      numa_node = NumaNode(node_index=numa_node_index, zones=[zone])
      numa_nodes[numa_node_index] = numa_node

  def read_buddy_info(self) -> BuddyInfoData:
    timestamp = int(time.time())
    numa_nodes = {}
    with open(self._BUDDY_INFO_PSEUDO_FILE) as fp:
      for line in fp:
        tokens = self._parse_line(line)
        self._parse_tokens(tokens, numa_nodes)

    return BuddyInfoData(
        timestamp=timestamp, numa_nodes=numa_nodes.values())

  def snapshot(self) -> None:
    assert self._output_file_object is not None
    self._snapshot_count += 1
    data = self.read_buddy_info()
    self._output_file_object.write(data.to_json() + '\n')

  def __enter__(self):
    self._output_file_object = self._output_path.open('wt')
    self._start_time = time.time()
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    if self._output_file_object:
      self._output_file_object.close()
    self._snapshot_count = 0

  @property
  def output_path(self) -> pathlib.Path:
    return self._output_path


class PsUtilLogger(BaseLogger):
  """Logger for Python `psutil` package.

  Note: Some metrics collected are only available on Linux.
  See https://psutil.readthedocs.io/en/latest/#system-related-functions
  for more info.
  """

  _CSV_HEADER = [
      # Process memory metrics
      'rss',
      'vms',
      'shared',
      'text',
      'lib',
      'data',
      'dirty',
      # Virtual memory metrics
      'vm_total',
      'vm_available',
      'vm_percent',
      'vm_used',
      'vm_free',
      'vm_active',
      'vm_inactive',
      'vm_buffers',
      'vm_cached',
      'vm_shared',
      'vm_slab',
      # Timestamp seconds since epoch
      'timestamp',
      # Throughput (snapshots/sec)
      'throughput',
  ]
  _OUTPUT_PREFIX = 'psutil-log'

  BYTES_TO_GIB = 1024 * 1024 * 1024

  def __init__(self, output_dir: str, label: Optional[str] = None):
    timestring = _get_timestring()
    csv_basename  = self._OUTPUT_PREFIX
    if label:
      csv_basename += f'-{label}'
    csv_basename += f'-{timestring}'
    self._output_path = (pathlib.Path(output_dir) /
                         csv_basename).with_suffix('.csv')

    self._vm_total = 0
    self._vm_available = 0
    self._start_time = 0
    self._snapshot_count = 0
    self._throughput = 0

  def __enter__(self):
    self._output_file_object = self._output_path.open('wt')
    self._csv_writer = csv.writer(self._output_file_object)
    self._csv_writer.writerow(self._CSV_HEADER)
    self._start_time = time.time()
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    if self._output_file_object:
      self._output_file_object.close()
    self._snapshot_count = 0

  def snapshot(self):
    assert self._csv_writer
    # Get process memory info
    p = psutil.Process()
    mem = p.memory_info()

    # Get system memory mem
    vm = psutil.virtual_memory()

    # Store latest snapshots
    self._vm_total = vm.total
    self._vm_available = vm.available

    timestamp = time.time()
    self._snapshot_count += 1
    self._throughput = self._snapshot_count / (timestamp - self._start_time)
    self._csv_writer.writerow([
        mem.rss,
        mem.vms,
        mem.shared,
        mem.text,
        mem.lib,
        mem.data,
        mem.dirty,
        self._vm_total,
        self._vm_available,
        vm.percent,
        vm.used,
        vm.free,
        vm.active,
        vm.inactive,
        vm.buffers,
        vm.cached,
        vm.shared,
        vm.slab,
        timestamp,
        self._throughput,
    ])

  @property
  def vm_total(self):
    """Returns total virtual memory from last snapshot.

    This should not change across snapshots.
    """
    return self._vm_total

  @property
  def vm_available(self):
    """Returns remaininng virtual memory available from last snapshot."""
    return self._vm_available

  @property
  def throughput(self):
    """Returns throughput from last snapshot."""
    return self._throughput

  @property
  def snapshot_count(self):
    return self._snapshot_count

  @property
  def output_path(self) -> pathlib.Path:
    return self._output_path


class MemoryLogger(BaseLogger):
  """Combination of different memory loggers."""

  SUPPORTED_LOGGERS = [
      BuddyInfoLogger,
      PsUtilLogger,
  ]

  def __init__(self, output_dir: str, label: Optional[str] = None):
    """Initialize."""
    self._loggers: Dict[str, BaseLogger] = {}
    for c in self.SUPPORTED_LOGGERS:
        self._loggers[c.__name__] = c(output_dir, label)

  def snapshot(self) -> None:
    """Takes a snapshot of memory allocation."""
    for name in self._loggers:
      self._loggers[name].snapshot()

  def __enter__(self):
    """Context manager `__enter__` method."""
    for name in self._loggers:
      self._loggers[name].__enter__()

  def __exit__(self, exc_type, exc_value, exc_tb):
    """Context manager `__exit__` method."""
    for name in self._loggers:
      self._loggers[name].__exit__()

