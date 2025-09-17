# Contributing to NautilusTrader

We highly value involvement from the trading community, and all contributions are greatly appreciated as they help us continually improve NautilusTrader!

## Steps

To contribute, follow these steps:

1. Open an issue on GitHub to discuss your proposed changes or enhancements.

2. Once everyone is aligned, fork the `develop` branch and ensure your fork is up-to-date by regularly merging any upstream changes.

3. Install and configure [pre-commit](https://pre-commit.com/) on your local machine to automatically run code checks, formatters, and linters before each commit.
   You can install pre-commit with:
    ```bash
    pip install pre-commit
    pre-commit install
    ```

4. Open a pull request (PR) on the `develop` branch with a summary comment and reference to any relevant GitHub issue(s).

5. The CI system will run the full test suite on your code including all unit and integration tests, so include appropriate tests with the PR.

6. Read and understand the Contributor License Agreement (CLA), available at https://github.com/nautechsystems/nautilus_trader/blob/develop/CLA.md.

7. You will also be required to sign the CLA, which is administered automatically through [CLA Assistant](https://cla-assistant.io/).

8. We will review your code as quickly as possible and provide feedback if any changes are needed before merging.

## Tips

- Follow the established coding practices in the [Developer Guide](https://nautilustrader.io/docs/developer_guide/index.html).
- For documentation changes, follow the style guide in `docs/developer_guide/docs.md` (use sentence case for headings H2 and below).
- Keep PRs small and focused for easier review.
- Reference the relevant GitHub issue(s) in your PR comment.

## Development environment setup

### Quick setup for contributors

For contributors who want to get started quickly with development:

1. **Fork and clone**: Fork the repository and clone your fork locally
2. **Use the development branch**: Always base your work on the `develop` branch
3. **Install development dependencies**: Run `make install-debug` for a debug build with all dependencies
4. **Run tests before committing**: Use `make pytest` to run the full test suite

### Code quality standards

We maintain high code quality standards through automated tooling:

- **Rust code**: All Rust code is formatted with `rustfmt` and linted with `clippy`
- **Python code**: We use `ruff` for formatting and linting Python code
- **Type checking**: Python code should include type hints where appropriate
- **Documentation**: All public APIs should be documented with docstrings

### Testing guidelines

When contributing code changes:

- **Unit tests**: Add unit tests for new functionality in the appropriate `tests/unit_tests/` directory
- **Integration tests**: For adapter or system-level changes, consider adding integration tests
- **Performance tests**: For performance-critical changes, run `make test-performance` to ensure no regressions
- **Cross-platform testing**: Consider how your changes might affect different operating systems

### Common contribution areas

New contributors often find these areas approachable:

- **Documentation improvements**: Fixing typos, adding examples, or clarifying existing documentation
- **Example strategies**: Contributing new example trading strategies or indicators
- **Bug fixes**: Addressing issues marked as "good first issue" in the GitHub issue tracker
- **Adapter enhancements**: Improving existing exchange adapters or adding support for new venues

### Getting help

If you need assistance while contributing:

- **Discord community**: Join our [Discord server](https://discord.gg/NautilusTrader) for real-time help
- **GitHub discussions**: Use GitHub Discussions for longer-form questions
- **Issue comments**: Comment on relevant issues if you need clarification on requirements
