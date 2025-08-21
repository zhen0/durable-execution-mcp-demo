# Run tests
test: build
    uv run --frozen pytest -xvs tests

# Run ty type checker on all files
typecheck:
    uv run --frozen ty check

# Copy context to clipboard
copy-context:
    uvx --with-editable . --refresh-package copychat copychat@latest src/ README.md -v