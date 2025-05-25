#!/bin/bash
echo "🚀 Applying .gitignore and cleaning tracked temp files..."

# Add .gitignore to Git tracking
git add .gitignore

# Remove unwanted tracked files (but keep them on disk)
git rm --cached -r __pycache__ || echo "No __pycache__ found"
git rm --cached *.txt 2>/dev/null || echo "No .txt files found"

# Commit the cleanup
git commit -m "Add .gitignore and remove tracked temp/cache files"

echo "✅ Done! Your Git repo is now clean and .gitignore is active."
