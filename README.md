# Python memory profiling utilities

This library contains tools to help collect memory usage and metrics in order to resolve memory leaks and other memory-related issues in your Python code.

This can be used to track memory usage over time and would be useful for analyzing how memory grows within successive iterations of a loop.

In particular, this could be used to measure memory usage of the TensorFlow data input pipeline based on tf.data, and see how changes to the pipeline operations could improve performance.

## Sample usage

```python
import tensorflow as tf
from memutil import logger as memlogger

input_dataset = tf.data.TFRecordDataset('/path/to/tfrecords/*', ...)
with memlogger.PsUtilLogger(output_dir='/tmp/output') as logger:
    for _ in input_dataset:
        logger.snapshot()
```

The above code snippet will take a memory snapshot with metrics from the `psutil` Python package and record that to a CSV file under the specified `output_dir` directory every iteration step of input_dataset.

## Installation

### Install from source
```bash
python setup.py install
```

## Memory loggers

The various memory metrics loggers such as `PsUtilLogger` can be found in `logger.py`.


## Testing

Install prerequisite packages in `requirements.txt` and `requirements-dev.txt`.

The unit tests are implemented using Python `unittest`, but they can be run
easily using `pytest`.

```bash
# cd to repo dir
pytest
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

## Disclaimer

This project is not an officially supported Google product.
