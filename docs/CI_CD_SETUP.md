# CI/CD Pipeline Setup

## Overview

This project uses GitHub Actions to automate releases, build Docker images, and manage semantic versioning.

## Workflow: Release and Build

File: `.github/workflows/release.yml`

### Trigger

The workflow is triggered on:
- **Push to main branch**: Automatically creates releases for commits to main
- **Manual trigger**: Can be run manually via GitHub Actions UI

### Jobs

#### 1. Version Generation (`version`)

**Purpose:** Automatically determines the next version based on conventional commits.

**How it works:**
1. Fetches the latest Git tag (e.g., `v0.1.0`)
2. Analyzes commit messages since the last tag
3. Determines version bump:
   - **Major** (X.0.0): Breaking changes
     - Commit messages with `feat!:` or `BREAKING CHANGE:`
     - Example: `feat!: redesign API` → `v0.1.0` → `v1.0.0`
   
   - **Minor** (0.X.0): New features
     - Commit messages with `feat:` or `feature:`
     - Example: `feat: add new audit tool` → `v0.1.0` → `v0.2.0`
   
   - **Patch** (0.0.X): Fixes and other changes
     - All other commits
     - Example: `fix: correct bug` → `v0.1.0` → `v0.1.1`

**Outputs:**
- `new_version`: e.g., `0.2.0`
- `new_tag`: e.g., `v0.2.0`
- `changelog`: List of commits since last release

#### 2. Build Python Package (`build`)

**Purpose:** Builds distributable Python packages.

**Steps:**
1. Sets up Python 3.12
2. Installs build tools (`build`, `twine`)
3. Updates version in `pyproject.toml` and `farofino_mcp/__init__.py`
4. Builds packages:
   - Source distribution (`.tar.gz`)
   - Wheel distribution (`.whl`)
5. Validates packages with `twine check`
6. Uploads packages as artifacts

**Outputs:**
- `farofino-mcp-{version}.tar.gz`
- `farofino_mcp-{version}-py3-none-any.whl`

#### 3. Build and Push Docker Image (`docker`)

**Purpose:** Creates and publishes Docker images to GitHub Container Registry.

**Steps:**
1. Sets up Docker Buildx (for advanced build features)
2. Logs in to GitHub Container Registry (ghcr.io)
3. Extracts metadata for tagging:
   - `latest`: Always points to the most recent release
   - `v{version}`: Version-specific tag (e.g., `v0.2.0`)
   - `{version}`: Short version tag (e.g., `0.2.0`)
4. Builds and pushes Docker image with multiple tags
5. Uses layer caching to speed up builds

**Image Tags:**
```
ghcr.io/italoag/farofino-mcp:latest
ghcr.io/italoag/farofino-mcp:v0.2.0
ghcr.io/italoag/farofino-mcp:0.2.0
```

#### 4. Create GitHub Release (`release`)

**Purpose:** Creates a GitHub release with changelog and artifacts.

**Steps:**
1. Downloads Python package artifacts
2. Creates a GitHub release with:
   - Tag name (e.g., `v0.2.0`)
   - Release name (e.g., `Release v0.2.0`)
   - Changelog from commits
   - Docker pull commands
   - Installation instructions
3. Attaches Python packages to the release

## Semantic Versioning

### Conventional Commits

Use these commit message formats:

#### Breaking Changes (Major version bump)
```bash
git commit -m "feat!: redesign API interface"
git commit -m "BREAKING CHANGE: remove deprecated methods"
```

#### New Features (Minor version bump)
```bash
git commit -m "feat: add support for new audit tool"
git commit -m "feature: implement caching mechanism"
```

#### Fixes and Other Changes (Patch version bump)
```bash
git commit -m "fix: correct pattern matching bug"
git commit -m "docs: update README"
git commit -m "chore: update dependencies"
```

### Version Flow Example

Starting from `v0.1.0`:

1. Commit: `fix: update pattern analysis` → `v0.1.1`
2. Commit: `feat: add new detector` → `v0.1.2` (already had minor bump)
3. Commit: `feat!: change tool interface` → `v1.0.0`

## Using the Pipeline

### Automatic Releases

Simply push to main:

```bash
git checkout main
git add .
git commit -m "feat: add new feature"
git push origin main
```

The pipeline will:
1. Determine the new version
2. Build Python packages
3. Build and push Docker image
4. Create a GitHub release

### Manual Releases

1. Go to GitHub repository
2. Click "Actions" tab
3. Select "Release and Build" workflow
4. Click "Run workflow"
5. Choose the branch (usually `main`)
6. Click "Run workflow"

## Outputs

After a successful release:

### 1. GitHub Release

- Visit: `https://github.com/italoag/farofino-mcp/releases`
- Contains:
  - Version tag
  - Changelog
  - Python packages (`.tar.gz`, `.whl`)
  - Installation instructions

### 2. Docker Images

Pull the latest image:
```bash
docker pull ghcr.io/italoag/farofino-mcp:latest
```

Or a specific version:
```bash
docker pull ghcr.io/italoag/farofino-mcp:0.2.0
```

### 3. Python Packages

Available as release assets, can be installed with:
```bash
pip install https://github.com/italoag/farofino-mcp/releases/download/v0.2.0/farofino-mcp-0.2.0.tar.gz
```

## Configuration

### Required Secrets

The workflow uses built-in GitHub secrets:
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
  - Used for creating releases
  - Used for pushing to GitHub Container Registry

### Optional Secrets

For Docker Hub (if desired):
- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token

To add these:
1. Go to repository "Settings"
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add each secret

## Monitoring

### Viewing Workflow Runs

1. Go to "Actions" tab in GitHub repository
2. Click on a specific workflow run
3. View logs for each job

### Troubleshooting

#### Version not incrementing

- Check that commits follow conventional commit format
- Ensure commits exist since the last tag

#### Docker build fails

- Check Docker image size limits
- Review build logs for dependency issues
- Verify network connectivity

#### Release creation fails

- Ensure `GITHUB_TOKEN` has write permissions
- Check that the tag doesn't already exist

## Local Testing

### Test version calculation

```bash
# Get current version
git describe --tags --abbrev=0

# View commits since last tag
git log v0.1.0..HEAD --pretty=format:"%s"
```

### Test Python package build

```bash
python -m build
twine check dist/*
```

### Test Docker build

```bash
docker build -t farofino-mcp:test .
docker run -i --rm farofino-mcp:test
```

## Best Practices

1. **Use conventional commits**: Always follow the format for automatic versioning
2. **Test locally first**: Build and test before pushing to main
3. **Small, focused commits**: Makes changelogs more readable
4. **Meaningful commit messages**: They become part of the release notes
5. **Review workflows**: Check the Actions tab after pushing

## Future Improvements

- [ ] Add automated testing before release
- [ ] Publish to PyPI automatically
- [ ] Add code quality checks (linting, type checking)
- [ ] Add security scanning for Docker images
- [ ] Generate more detailed changelogs with categories
- [ ] Add rollback mechanism for failed releases

## Support

For issues with the CI/CD pipeline:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Open an issue: https://github.com/italoag/farofino-mcp/issues
