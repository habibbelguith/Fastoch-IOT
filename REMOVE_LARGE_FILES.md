# Remove Large Files from Git History

## Problem
GitHub rejected your push because these files exceed 100 MB:
- `lapi.weights` (233.83 MB)
- `Attachments.zip` (445.24 MB)

These files are in your git history, so we need to remove them from ALL commits.

## Solution: Use git filter-branch

### Step 1: Install git-filter-repo (Recommended) or use filter-branch

**Option A: Using git filter-branch (Built-in)**

```powershell
# Remove lapi.weights from all commits
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch 'Deep-Learning/Licence_plate_detection/lapi.weights'" --prune-empty --tag-name-filter cat -- --all

# Remove Attachments.zip from all commits
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch 'Deep-Learning/Licence_plate_detection/Attachments.zip'" --prune-empty --tag-name-filter cat -- --all

# Remove Attachments directory from all commits
git filter-branch --force --index-filter "git rm -r --cached --ignore-unmatch 'Deep-Learning/Licence_plate_detection/Attachments/'" --prune-empty --tag-name-filter cat -- --all

# Remove model files
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch 'Deep-Learning/Licence_Plate_Recognition/ocrmodel.h5'" --prune-empty --tag-name-filter cat -- --all
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch 'Deep-Learning/Main-Scripts/ocrmodel.h5'" --prune-empty --tag-name-filter cat -- --all
```

### Step 2: Clean up and force push

```powershell
# Clean up backup refs
git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object { git update-ref -d $_ }

# Force garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: This rewrites history!)
git push origin --force --all
```

## Alternative: Simpler Approach (If you don't mind losing history)

If this is a new repository and you don't need the commit history:

```powershell
# Create a new orphan branch
git checkout --orphan new-main

# Add all files (large files will be ignored by .gitignore)
git add .

# Commit
git commit -m "Initial commit without large files"

# Delete old main branch
git branch -D main

# Rename current branch to main
git branch -m main

# Force push
git push -f origin main
```

## Recommended: Use BFG Repo-Cleaner (Easier)

1. Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
2. Run:

```powershell
# Clone a fresh copy
cd ..
git clone --mirror https://github.com/habibbelguith/Fastoch-IOT.git temp-repo.git

# Remove large files
java -jar bfg.jar --delete-files "lapi.weights" temp-repo.git
java -jar bfg.jar --delete-files "Attachments.zip" temp-repo.git
java -jar bfg.jar --delete-folders "Attachments" temp-repo.git

# Clean up
cd temp-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Push
git push
```

## Quick Fix (Simplest - If repository is new)

If you just started and don't care about history:

```powershell
# 1. Make sure .gitignore is correct (already done)
git add .gitignore
git commit -m "Add .gitignore"

# 2. Remove large files from current commit
git rm --cached "Deep-Learning/Licence_plate_detection/lapi.weights"
git rm --cached "Deep-Learning/Licence_plate_detection/Attachments.zip"
git rm -r --cached "Deep-Learning/Licence_plate_detection/Attachments/"

# 3. Commit removal
git commit -m "Remove large files"

# 4. If files are in previous commits, use filter-branch (see above)
```

## After Removing Files

1. **Verify files are removed:**
   ```powershell
   git ls-files | Select-String "\.weights|\.zip|\.h5"
   ```

2. **Check repository size:**
   ```powershell
   git count-objects -vH
   ```

3. **Push:**
   ```powershell
   git push origin main
   ```

## Important Notes

⚠️ **Warning:** Removing files from git history rewrites history. If others have cloned the repo, they'll need to re-clone.

✅ **Files stay on your computer** - they're just removed from git tracking.

📝 **Add to README:** Mention that users need to download `lapi.weights` separately (as you already do).

