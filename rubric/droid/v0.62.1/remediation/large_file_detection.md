---
signal_name: Large File Detection
---

## Criterion-Specific Fix Guidance

- **Git LFS**: Install Git LFS (`git lfs install`) and track large file types via `.gitattributes`. Common patterns: `*.bin`, `*.zip`, `*.tar.gz`, `*.model`, `*.weights`, `*.psd`, `*.dll`, `*.so`, `*.dylib`. Add lines like `*.bin filter=lfs diff=lfs merge=lfs -text` to `.gitattributes` and commit it.
- **Pre-commit hook**: Add a file-size check using `pre-commit`. In `.pre-commit-config.yaml`, add the `check-added-large-files` hook from `pre-commit/pre-commit-hooks` with `args: ['--maxkb=500']` (adjust threshold as needed).
- **CI enforcement**: Add a CI step that fails on large files. Example: `find . -not -path './.git/*' -size +1M -type f` and fail if output is non-empty. Or use `git diff --cached --diff-filter=d --name-only | xargs -I{} du -k {} | awk '$1 > 500'` for staged files.
- **Linter rules**: Tools like `mega-linter` and `trunk check` include large-file detection. Configure the threshold in their respective config files.
- **.gitignore**: Ensure common large binary directories (`node_modules/`, `dist/`, `build/`, `*.egg-info/`, `__pycache__/`) are in `.gitignore` to prevent accidental commits.
- **Retroactive cleanup**: If large files already exist in history, use `git-filter-repo` or BFG Repo Cleaner to remove them, then set up prevention going forward.

## Criterion-Specific Exploration Steps

- Check for `.gitattributes` at the repo root and look for LFS filter entries
- Check for `.pre-commit-config.yaml` and look for `check-added-large-files` hook
- Check CI workflow files (`.github/workflows/*.yml`) for file-size checks
- Look for large files already in the repo: `git ls-files | xargs du -k | sort -rn | head -20`
- Check if Git LFS is initialized: `git lfs ls-files` (will error if LFS not installed)

## Criterion-Specific Verification Steps

- Confirm `.gitattributes` exists and contains LFS tracking rules, OR `.pre-commit-config.yaml` contains `check-added-large-files`, OR CI has a file-size gate
- Test the pre-commit hook by staging a large file and running `pre-commit run check-added-large-files`
- Run `git lfs ls-files` to confirm LFS is tracking the expected file types
