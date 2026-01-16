# Antigravity AI - GitHub Backup Script

This script provides automated backup functionality for the Antigravity AI codebase to GitHub.

## Features

- ✅ Automatic git add/commit/push workflow
- ✅ Multiple backup types (full, incremental, config, data)
- ✅ Custom commit messages and branch support
- ✅ Comprehensive error handling and logging
- ✅ Colored output for better readability
- ✅ Local commit option (no push)
- ✅ Status checking without backup

## Prerequisites

1. **Git Repository**: Ensure you're in a git repository
2. **GitHub Remote**: Configure a GitHub remote repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   ```
3. **Authentication**: Set up GitHub authentication (token, SSH key, etc.)

## Usage

### Basic Usage

```bash
# Incremental backup (default)
./backup_to_github.sh

# Full backup
./backup_to_github.sh -t full

# Config-only backup
./backup_to_github.sh -t config

# Data backup (logs, data files)
./backup_to_github.sh -t data
```

### Advanced Options

```bash
# Custom commit message
./backup_to_github.sh -m "Emergency backup before major changes"

# Push to different branch
./backup_to_github.sh -b develop

# Commit locally only (no push)
./backup_to_github.sh -n

# Show git status without backup
./backup_to_github.sh -s

# Combined options
./backup_to_github.sh -t config -m "Updated model configurations" -b staging
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--type` | `-t` | Backup type: `full`, `incremental`, `config`, `data` |
| `--branch` | `-b` | Target branch (default: `main`) |
| `--message` | `-m` | Custom commit message |
| `--no-push` | `-n` | Commit locally only, skip push |
| `--status` | `-s` | Show git status and exit |
| `--help` | `-h` | Show help message |

## Backup Types

### Full Backup (`-t full`)
- Backs up entire codebase
- Includes all files, configurations, and data
- Best for complete snapshots

### Incremental Backup (`-t incremental`) [Default]
- Backs up current changes
- Standard development workflow
- Most common usage

### Config Backup (`-t config`)
- Focuses on configuration files
- Includes YAML, JSON, and config files
- Useful for settings backups

### Data Backup (`-t data`)
- Focuses on data and log files
- Includes data directories and log files
- Useful for preserving runtime data

## Examples

### Daily Development Backup
```bash
# In your development workflow
./backup_to_github.sh -m "Daily backup: $(date)"
```

### Pre-Deployment Backup
```bash
# Before major changes
./backup_to_github.sh -t full -m "Pre-deployment backup"
```

### Configuration Changes
```bash
# After updating configs
./backup_to_github.sh -t config -m "Updated AI model configurations"
```

### Local Testing
```bash
# Test changes locally without pushing
./backup_to_github.sh -n -m "Local test commit"
```

## Output Examples

### Successful Backup
```
[INFO] Starting GitHub backup process...
[INFO] Backup type: incremental
[INFO] Found uncommitted changes
[INFO] Adding files to git...
[SUCCESS] Files added successfully
[INFO] Committing changes with message: Auto-backup: 2024-01-16_14-30-15
[SUCCESS] Changes committed successfully
[INFO] Pushing to remote branch: main
[SUCCESS] Successfully pushed to GitHub
[SUCCESS] Backup completed successfully!
```

### No Changes
```
[INFO] Starting GitHub backup process...
[WARNING] No changes to commit
[INFO] No changes to backup. Exiting.
```

### Error Handling
```
[ERROR] No remote repository configured. Please set up a GitHub remote first:
[ERROR]   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

## Troubleshooting

### Common Issues

1. **"Not a git repository"**
   - Ensure you're running the script from the project root
   - Initialize git if needed: `git init`

2. **"No remote repository configured"**
   - Add GitHub remote: `git remote add origin <repository-url>`
   - Verify remote: `git remote -v`

3. **Authentication failed**
   - Use GitHub token or SSH key
   - Check credentials: `git config --list`

4. **Permission denied**
   - Ensure script is executable: `chmod +x backup_to_github.sh`
   - Check file permissions

### Debug Mode

Add debug logging by modifying the script:
```bash
# Add at top of script
set -x  # Enable debug tracing
```

## Integration

### Cron Job (Automated Backups)
```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /path/to/antigravity-ai/backup_to_github.sh -m "Automated daily backup"
```

### Git Hooks
```bash
# In .git/hooks/post-commit
#!/bin/sh
/path/to/antigravity-ai/backup_to_github.sh -n -m "Post-commit backup"
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Backup to GitHub
  run: ./backup_to_github.sh -t full -m "CI/CD backup: ${{ github.run_id }}"
```

## Security Notes

- Never commit sensitive data (API keys, passwords)
- Use `.gitignore` to exclude sensitive files
- Consider using GitHub's private repositories for sensitive codebases
- Review committed files before pushing

## License

This script is part of the Antigravity AI project.