---
description: Delete files only with the trash shell command — never rm or the Delete tool
alwaysApply: true
---

# File deletion — trash command only

When removing files or directories, **always** use the macOS `trash` CLI via the **Shell** tool. This applies to cleanup, refactors, temp files, and build artifacts.

## Required workflow

1. Tell the user the **exact path(s)** to remove (unless they already asked to delete those paths).
2. Wait for **explicit approval** before running `trash` (unless the user already approved those paths in the same request).
3. Run only:

```bash
trash "/absolute/path/to/file_or_directory"
```

Use absolute paths when possible. Multiple paths: `trash path1 path2`.

## Forbidden — never use these to delete

- `rm`, `rm -f`, `rm -r`, `rm -rf`, or any `rm` variant
- The **Delete** tool (permanent removal, not macOS Trash)
- `unlink`, `find ... -delete`, or other hard-delete shell patterns
- Emptying Trash programmatically without user request

## If trash is missing

Ask the user to install it (`brew install trash` on macOS). **Do not** fall back to `rm` or the Delete tool.

## Examples

```bash
# GOOD
trash "/Users/apple/Desktop/Assembly_Language_x86/Final exam data/_ch8_main_fragment.html"

# BAD — permanent delete
rm "Final exam data/old_file.html"

# BAD — Delete tool
# (do not call Delete with path: ...)
```
