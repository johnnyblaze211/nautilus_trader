# Getting Started

To get started with NautilusTrader, you will need:

- A Python 3.11–3.13 environment with the `nautilus_trader` package installed.
- A way to run Python scripts or Jupyter notebooks for backtesting and/or live trading.

## [Installation](installation.md)

The **Installation** guide will help to ensure that NautilusTrader is properly installed on your machine.

## [Quickstart](quickstart.md)

The **Quickstart** provides a step-by-step walk through for setting up your first backtest.

## Examples in repository

The [online documentation](https://nautilustrader.io/docs/latest/) shows just a subset of examples. For the full set, see this repository on GitHub.

The following table lists example locations ordered by recommended learning progression:

| Directory                   | Contains                                                                                                                    |
|:----------------------------|:----------------------------------------------------------------------------------------------------------------------------|
| [examples/](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples)                 | Fully runnable, self-contained Python examples.                                                                                     |
| [docs/tutorials/](tutorials/)           | Jupyter notebook tutorials demonstrating common workflows.                                                                              |
| [docs/concepts/](concepts/)            | Concept guides with concise code snippets illustrating key features. |
| [nautilus_trader/examples/](../nautilus_trader/examples/) | Pure-Python examples of basic strategies, indicators, and execution algorithms.                                     |
| [tests/unit_tests/](../../tests/unit_tests/)         | Unit tests covering core functionality and edge cases.                      |

## Backtesting API levels

NautilusTrader provides two different API levels for backtesting:

| API Level      | Description                           | Characteristics                                                                                                                                                                                                                                                                                                                                                        |
|:---------------|:--------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| High-Level API | Uses `BacktestNode` and `TradingNode` | Recommended for production: easier transition to live trading; requires a Parquet-based data catalog. |
| Low-Level API  | Uses `BacktestEngine`                 | Intended for library development: no live-trading path; direct component access; may encourage non–live-compatible patterns. |

Backtesting involves running simulated trading systems on historical data.

To get started backtesting with NautilusTrader you need to first understand the two different API
levels which are provided, and which one may be more suitable for your intended use case.

:::info
For more information on which API level to choose, refer to the [Backtesting](../concepts/backtesting.md) guide.
:::

### [Backtest (low-level API)](backtest_low_level.md)

This tutorial runs through how to load raw data (external to Nautilus) using data loaders and wranglers,
and then use this data with a `BacktestEngine` to run a single backtest.

### [Backtest (high-level API)](backtest_high_level.md)

This tutorial runs through how to load raw data (external to Nautilus) into the data catalog,
and then use this data with a `BacktestNode` to run a single backtest.

## Running in docker

Alternatively, you can download a self-contained dockerized Jupyter notebook server, which requires no setup or
installation. This is the fastest way to get up and running to try out NautilusTrader. Note that deleting the container will also delete any data.

- To get started, install docker:
  - Go to [Docker installation guide](https://docs.docker.com/get-docker/) and follow the instructions.
- From a terminal, download the latest image:
  - `docker pull ghcr.io/nautechsystems/jupyterlab:nightly --platform linux/amd64`
- Run the docker container, exposing the jupyter port:
  - `docker run -p 8888:8888 ghcr.io/nautechsystems/jupyterlab:nightly`
- Open your web browser to `localhost:{port}`:
  - <http://localhost:8888>

:::info
NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output),
therefore we set `log_level` to `ERROR` in the examples. Lowering this level to see
more logging will cause the notebook to hang during cell execution. We are currently
investigating a fix that involves either raising the configured rate limits for
Jupyter, or throttling the log flushing from Nautilus.

- <https://github.com/jupyterlab/jupyterlab/issues/12845>
- <https://github.com/deshaw/jupyterlab-limit-output>

:::

## Common workflows and troubleshooting

### Development workflow recommendations

When developing trading strategies with NautilusTrader, we recommend following this iterative workflow:

1. **Start with the high-level API**: Use `BacktestNode` for initial strategy development as it provides a cleaner path to live trading
2. **Use version control**: Always commit your strategy code and configuration files to track changes and performance variations
3. **Test incrementally**: Begin with small datasets and short time periods before scaling to full historical backtests
4. **Validate data quality**: Always inspect your data for gaps, outliers, or inconsistencies before running backtests

### Common installation issues

**Issue**: Import errors after installation
```python
ImportError: No module named 'nautilus_trader'
```
**Solution**: Ensure you're using the correct Python environment and that the package was installed successfully:
```bash
pip list | grep nautilus
python -c "import nautilus_trader; print(nautilus_trader.__version__)"
```

**Issue**: Performance degradation on Windows
**Solution**: Windows users should be aware that NautilusTrader runs in standard-precision mode (64-bit) due to platform limitations. For high-precision requirements, consider using Linux or macOS environments.

**Issue**: Memory issues with large datasets
**Solution**: Use data streaming and chunking techniques. Consider using the data catalog's built-in pagination features for large historical datasets.

### Performance optimization tips

- **Use Cython for custom indicators**: For latency-sensitive applications, implement custom indicators in Cython rather than pure Python
- **Optimize data loading**: Use Parquet format for historical data storage as it provides better compression and faster I/O
- **Configure logging appropriately**: Use `INFO` or `WARNING` log levels in production to reduce I/O overhead
- **Monitor memory usage**: Large backtests can consume significant memory; consider using data streaming for very large datasets
