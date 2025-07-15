# Developer Guide: Publishing to PyPI

**For maintainers only** - how to release new versions of the package.

## One-Time Setup

### 1. Get PyPI Token
1. Go to https://pypi.org/manage/account/token/
2. Create new token (scope: "Entire account" or specific project)
3. Copy the token (starts with `pypi-`)

### 2. Configure Credentials
Create `~/.pypirc`:
```ini
[pypi]
  username = __token__
  password = pypi-YOUR_TOKEN_HERE
```

## Release Process

### Every Release (3 Commands)

```bash
# 1. Bump version in pyproject.toml
# Edit: version = "0.2.0" (increment as needed)

# 2. Clean build
rm -rf dist/ && uv build

# 3. Publish
TOKEN=$(grep password ~/.pypirc | sed 's/.*= //') && uv publish --token "$TOKEN"
```

**That's it!** Package is live at https://pypi.org/project/teamcenter-mcp-server/

## Version Strategy

- **Patch** (0.2.X): Bug fixes, documentation updates
- **Minor** (0.X.0): New features, API additions  
- **Major** (X.0.0): Breaking changes

## Verification

Test the published package:
```bash
uvx teamcenter-mcp-server --version
```

## Troubleshooting

**"Missing credentials"**: Check `~/.pypirc` format  
**"403 Forbidden"**: Token expired - create new one  
**"File already exists"**: Forgot to bump version number

## Files That Matter

- `pyproject.toml`: Version number and package config
- `README.md`: Shows on PyPI page
- `auth_mcp_stdio_v2.py`: Main code
- `~/.pypirc`: Your PyPI credentials (local only)

**Remember**: Every PyPI release is permanent. Test locally first!