# Memory Leak Tests Refactoring

This document describes the refactoring of the memory leak test files to improve maintainability, readability, and code organization.

## Refactoring Overview

The memory leak tests have been refactored to extract common functionality into shared modules while maintaining the same directory structure and keeping the original test files intact but improved.

## New Structure

### Shared Modules

#### `test_fixtures.py`
- **Purpose**: Centralized test fixtures and configurations
- **Contents**:
  - `TestInstruments`: Common test instruments (AUDUSD_SIM, GBPUSD_SIM, ETHUSDT_BINANCE)
  - `TestConfigurations`: Shared backtest configurations and strategy configs
  - `TestDataWranglers`: Common data wranglers for different data types
  - `setup_catalog_with_data()`: Catalog setup utility
  - `get_catalog_backtest_config()`: Backtest configuration for catalog tests
  - `cleanup_catalog()`: Catalog cleanup utility

#### `memory_utils.py`
- **Purpose**: Memory monitoring and testing utilities
- **Contents**:
  - `MemoryMonitor`: Class for tracking memory usage across test runs
  - `snapshot_memory()`: Decorator for memory monitoring (backward compatible)
  - `run_memory_test()`: High-level function for running memory leak tests

### Refactored Test Files

#### `conftest.py` (Simplified)
- **Before**: 83 lines with embedded memory monitoring logic
- **After**: 47 lines with imports from shared utilities
- **Changes**:
  - Extracted memory monitoring logic to `memory_utils.py`
  - Maintained backward compatibility
  - Added clear documentation

#### `memray_backtest.py` (Improved Organization)
- **Before**: 103 lines with inline configuration and setup
- **After**: 108 lines with better structure and shared utilities
- **Changes**:
  - Extracted configuration setup to shared utilities
  - Separated concerns into focused functions:
    - `setup_backtest_engine()`: Engine configuration
    - `add_test_data()`: Data setup
    - `add_strategy_and_algorithm()`: Strategy configuration
    - `run_single_backtest()`: Single test iteration
  - Uses `run_memory_test()` for consistent memory monitoring

#### `memray_backtest_catalog.py` (Significantly Simplified)
- **Before**: 143 lines with complex inline catalog setup
- **After**: 62 lines using shared utilities
- **Changes**:
  - Moved catalog setup logic to `test_fixtures.py`
  - Simplified main test function to focus on the test logic
  - Better error handling and cleanup
  - Uses shared configuration utilities

#### `memray_data.py` (Better Organization)
- **Before**: 62 lines with inline data processing
- **After**: 85 lines with separated concerns
- **Changes**:
  - Separated data processing into focused functions:
    - `process_quote_ticks()`: Quote tick processing
    - `process_trade_ticks()`: Trade tick processing
    - `process_bar_data()`: Bar data processing
  - Uses shared data wranglers and instruments
  - Better memory cleanup with explicit `del` statements

## Benefits of Refactoring

### 1. **Improved Maintainability**
- Common configurations centralized in `test_fixtures.py`
- Memory monitoring logic centralized in `memory_utils.py`
- Easier to update shared functionality across all tests

### 2. **Better Readability**
- Clear separation of concerns
- Well-documented functions with specific purposes
- Consistent naming conventions and structure

### 3. **Reduced Code Duplication**
- Shared instrument definitions
- Common configuration patterns
- Reusable memory monitoring utilities

### 4. **Enhanced Testability**
- Modular functions that can be tested independently
- Clear interfaces between components
- Better error handling and cleanup

### 5. **Backward Compatibility**
- Existing imports continue to work
- Original functionality preserved
- Gradual migration path for existing code

## Usage Examples

### Using Shared Fixtures
```python
from tests.mem_leak_tests.test_fixtures import TestInstruments, TestConfigurations

# Get common test instruments
instrument = TestInstruments.get_ethusdt_binance()

# Get shared configurations
config = TestConfigurations.get_basic_backtest_engine_config()
```

### Using Memory Utilities
```python
from tests.mem_leak_tests.memory_utils import run_memory_test

def my_test_function():
    # Your test logic here
    pass

# Run memory leak test
run_memory_test(
    test_func=my_test_function,
    runs=128,
    test_name="My Memory Leak Test"
)
```

### Using Data Wranglers
```python
from tests.mem_leak_tests.test_fixtures import TestDataWranglers

# Get pre-configured wranglers
trade_wrangler = TestDataWranglers.get_trade_tick_wrangler()
quote_wrangler = TestDataWranglers.get_quote_tick_wrangler()
```

## File Size Comparison

| File | Before (lines) | After (lines) | Change |
|------|----------------|---------------|---------|
| `conftest.py` | 83 | 47 | -36 (-43%) |
| `memray_backtest.py` | 103 | 108 | +5 (+5%) |
| `memray_backtest_catalog.py` | 143 | 62 | -81 (-57%) |
| `memray_data.py` | 62 | 85 | +23 (+37%) |
| **New Files** | | | |
| `test_fixtures.py` | 0 | 244 | +244 |
| `memory_utils.py` | 0 | 142 | +142 |
| **Total** | 391 | 688 | +297 (+76%) |

While the total line count increased due to the addition of shared modules, the individual test files are now more focused and maintainable. The shared modules provide significant value through reusability and better organization.

## Migration Guide

### For Existing Code
- No changes required for basic usage
- `conftest.py` imports remain the same
- All original functionality preserved

### For New Tests
- Use `test_fixtures.py` for common configurations
- Use `memory_utils.run_memory_test()` for consistent memory testing
- Follow the pattern established in refactored files

## Future Improvements

1. **Additional Shared Utilities**: More common patterns can be extracted as they emerge
2. **Configuration Management**: Environment-specific configurations could be centralized
3. **Test Data Management**: Common test data setup and cleanup utilities
4. **Performance Benchmarking**: Integration with performance monitoring tools
5. **Automated Memory Leak Detection**: Integration with CI/CD pipelines for automated detection

## Conclusion

This refactoring improves the maintainability and readability of the memory leak tests while preserving all existing functionality. The new structure makes it easier to add new tests, maintain existing ones, and ensure consistency across the test suite.
