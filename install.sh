#!/usr/bin/env bash
# Installer script for Skilly (Bash/Zsh/POSIX)
# Symlinks `skilly` to a directory in your PATH (e.g., ~/.local/bin or /usr/local/bin)

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILLY_BIN="$DIR/bin/skilly"

chmod +x "$SKILLY_BIN"
chmod +x "$DIR/skilly"

# Target bin directory
if [ -d "$HOME/.local/bin" ]; then
  TARGET_DIR="$HOME/.local/bin"
elif [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
  TARGET_DIR="/usr/local/bin"
else
  TARGET_DIR="$HOME/.local/bin"
  mkdir -p "$TARGET_DIR"
fi

ln -sf "$SKILLY_BIN" "$TARGET_DIR/skilly"

echo "============================================="
echo "  ⚡ Skilly installed successfully!"
echo "  Linked: $TARGET_DIR/skilly -> $SKILLY_BIN"
echo "============================================="
echo ""
echo "Make sure '$TARGET_DIR' is in your PATH. If needed, add this to your ~/.bashrc or ~/.zshrc:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Usage:"
echo "  skilly <project_directory>"
echo "  skilly ."
echo "  skilly my-project --serve"
