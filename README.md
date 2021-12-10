# ci-cd

This repo houses the Zooniverse's shared CI/CD templates, actions, and workflows.

## Workflows

Call these workflows externally from other apps/repos like in this example for running RSpec tests in a Rails app:

```yaml
name: Run Rspec

on:
  pull_request:
  workflow_dispatch:

jobs:
  run_rspec:
    name: Run Rspec Tests
    uses: zooniverse/ci-cd/.github/workflows/run_rspec.yaml@main
    with:
      db_name: app_db_test
      ruby_version: 2.6.5
```