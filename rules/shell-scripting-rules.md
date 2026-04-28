# Shell Scripting Standards & Best Practices

## 1. Introduction
This document provides guidelines for writing robust, readable, and maintainable shell scripts. These standards apply to `bash` and other POSIX-compliant shells.

## 2. Script Header
All scripts MUST start with a shebang and a brief description of their purpose.

```bash
#!/bin/bash
#
# This script automates the deployment of the web application.
# It handles building the project, pushing to the registry, and deploying.
```

## 3. Best Practices
- **Unofficial Strict Mode**: Start all scripts with `set -euo pipefail` to catch common errors.
  - `set -e`: Exit immediately if a command exits with a non-zero status.
  - `set -u`: Treat unset variables as an error when substituting.
  - `set -o pipefail`: The return value of a pipeline is the status of the last command to exit with a non-zero status, or zero if no command exited with a non-zero status.
- **Variable Quoting**: Always quote variables (`"$VAR"`) to prevent word splitting and globbing issues.
- **Use `[[ ... ]]`**: Prefer `[[ ... ]]` over `[ ... ]` for tests, as it is more robust and feature-rich.
- **Variable Naming**: Use `UPPER_SNAKE_CASE` for global constants and `lower_snake_case` for local variables.
- **Use `local`**: Declare variables inside functions with the `local` keyword to limit their scope.
- **Error Messages**: Print error messages to `stderr`.
  ```bash
  echo "Error: Something went wrong." >&2
  exit 1
  ```
- **Functions**: Break down complex scripts into smaller, reusable functions.

## 4. Readability
- **Comments**: Add comments to explain complex parts of the script.
- **Indentation**: Use consistent indentation (2 or 4 spaces).
- **Long Lines**: Break long lines for readability using a backslash (`\`).

## Example Script
```bash
#!/bin/bash
set -euo pipefail

readonly PROJECT_NAME="my-app"
readonly DOCKER_REGISTRY="my-registry.com"

main() {
  local version
  version=$(get_version)

  echo "Starting deployment for $PROJECT_NAME version $version..."

  build_image "$version"
  push_image "$version"

  echo "Deployment successful."
}

get_version() {
  local tag
  tag=$(git describe --tags --abbrev=0)
  echo "$tag"
}

build_image() {
  local version="$1"
  docker build -t "$DOCKER_REGISTRY/$PROJECT_NAME:$version" .
}

push_image() {
  local version="$1"
  docker push "$DOCKER_REGISTRY/$PROJECT_NAME:$version"
}

main "$@"
