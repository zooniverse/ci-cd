# ci-cd

This repo houses the Zooniverse's shared CI/CD templates, actions, and workflows.

Minimize ops & CI/CD code repetition and drift by calling these shared workflows from your repo. Use the latest version by specifying the `@main` tag, or pin to a specific commit or branch name.

## Examples

### Run RSpec tests in a Rails app:
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

### Build and push a Docker image to GHCR
This is useful for ensuring that an image exists before a deploy & migrate. This example will build on every pull request update, but this workflow can also be used as a part of larger deploy jobs to avoid excessive building. You can also optionally add the `latest` tag (defaults to false) if you're updating on push to master. Extra build arguments can be specified with `build-args`, sent as a string.

```yaml
name: Build and Push Image

on:
  pull_request:
  workflow_dispatch:

jobs:
  build_and_push_image:
    name: Build and Push Image
    uses: zooniverse/ci-cd/.github/workflows/build_and_push_image.yaml@main
    with:
      repo_name: education-api
      commit_id: ${{ github.sha }}
      latest: true
      build_args: |
        APP_ENV=staging
```

### Deploy a Rails app in Kubernetes
This is a staging deploy (push to master) that would likely also need a Docker build/push (above) and a database migration (below).
```yaml
on:
  push:
    branches:
      - master

  deploy_staging:
    name: Deploy to Staging
    uses: zooniverse/ci-cd/.github/workflows/deploy_app.yaml@main
    with:
      app_name: myapp
      repo_name: myapp
      commit_id: ${{ github.sha }}
      environment: staging
    secrets:
      creds: ${{ secrets.AZURE_AKS }}
```

### Build and deploy a static site
```yaml
name: Deploy App to Production
on:
  # Run this workflow on push to production-release tag (via chatops)
  push:
    tags:
      - production-release

jobs:
  build:
    uses: zooniverse/ci-cd/.github/workflows/npm_build.yaml@main
    with:
      commit_id: ${{ github.sha }}
      node_version: '16.x'
      # The name of the build artifact to store
      output: 'dist'
      # The name of the npm build script to run
      script: '_build-production'
  deploy:
    name: Deploy production
    uses: zooniverse/ci-cd/.github/workflows/deploy_static.yaml@main
    needs: build
    with:
      # Retrieve the build artifact
      source: 'dist'
      target: 'myapp.zooniverse.org'
    secrets:
      creds: ${{ secrets.AZURE_STATIC_SITES }}
```

### Send a Slack notification
```yaml
slack_notification:
  name: Send Slack notification
  uses: zooniverse/ci-cd/.github/workflows/slack_notification.yaml@main
  # The name of the job to be reported on, e.g. deploy, run_rspec
  needs: deploy
  if: always()
  with:
    commit_id: ${{ github.sha }}
    # Use job name here also
    job_name: Build production / build
    status: ${{ needs.deploy.result }}
    # Customize the slack message
    title: 'My App Production deploy complete'
    title_link: 'https://myapp.zooniverse.org'
  secrets:
    slack_webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Run something in a Kubernetes pod, like a Rails rake task or a migration

These require a corresponding Kubernetes template in the app's `/kubernetes` folder. This will instantiate a new Job pod with the same image as the current deployment. It will run the specified action and log the results in the runner's console. Use the Slack notification workflow above to report its status to chat. Azure credentials are required for these, as they manage these AKS deployments. In the case of a deploy, you can ensure a migration finishes successfully by including `needs: migration_step_name`.

DB Migration:
```yaml
name: Production DB Migration

on:
  push:
    tags:
      - production-release
  workflow_dispatch:

jobs:
  db_migration_production:
    name: Production DB Migration
    uses: zooniverse/ci-cd/.github/workflows/db_migration.yaml@main
    # Ensure the deploy job successfully updates the deployment pod
    needs: deploy_production
    with:
      app_name: myapp
      environment: production
      commit_id: ${{ github.sha }}
    secrets:
      creds: ${{ secrets.AZURE_AKS }}
```

Rails/rake task with an input, manual only:
```yaml
name: Run Production Task

on:
  workflow_dispatch:
    inputs:
      task:
        description: Task to run
        required: true
        default: 'routes'

jobs:
  run_production_task:
    name: Run Production Task
    uses: zooniverse/ci-cd/.github/workflows/run_task.yaml@main
    with:
      app_name: myapp
      task_name: ${{ github.event.inputs.task }}
      environment: production
    secrets:
      creds: ${{ secrets.AZURE_AKS }}
```
