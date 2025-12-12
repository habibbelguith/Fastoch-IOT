# Fix Git Push Issue - Large Files

## Problem
Your git push is stuck because you're trying to upload 716 MB of large files (model files, weights, ZIP files) that shouldn't be in git.

## Solution Steps

### Step 1: Cancel the Current Push

Press `Ctrl+C` in your terminal to cancel the stuck push.

### Step 2: Remove Large Files from Git

Run these commands to remove large files from git tracking:

```powershell
# Remove model files
git rm --cached Deep-Learning/Licence_Plate_Recognition/ocrmodel.h5
git rm --cached Deep-Learning/Main-Scripts/ocrmodel.h5

# Remove weight files
git rm --cached Deep-Learning/Licence_plate_detection/lapi.weights
git rm --cached "Deep-Learning/Licence_plate_detection/Attachments/Attachments/model.weights"

# Remove ZIP files
git rm --cached "Deep-Learning/Licence_plate_detection/Attachments.zip"

# Remove entire Attachments directory if it's tracked
git rm -r --cached "Deep-Learning/Licence_plate_detection/Attachments/"

# Remove output files
git rm -r --cached Deep-Learning/output/
git rm -r --cached Deep-Learning/uploads/
```

### Step 3: Add .gitignore

The .gitignore file has been created. Add it:

```powershell
git add .gitignore
```

### Step 4: Commit Changes

```powershell
git commit -m "Remove large files and add .gitignore"
```

### Step 5: Push Again

```powershell
git push -u origin main
```

This should now work much faster!

---

## Alternative: If Files Are Already in Git History

If the files are already in previous commits, you may need to clean git history:

```powershell
# Use git filter-branch or BFG Repo-Cleaner
# This is more advanced - only if needed
```

---

## What Should NOT Be in Git

- ✅ Model files (.h5, .weights)
- ✅ ZIP files
- ✅ Output images
- ✅ Large datasets
- ✅ Virtual environments

## What SHOULD Be in Git

- ✅ Source code (.py files)
- ✅ Configuration files
- ✅ README.md
- ✅ requirements.txt
- ✅ Small test images (if needed)

---

## Quick Fix Commands (Copy-Paste)

```powershell
# 1. Cancel current push (Ctrl+C if still running)

# 2. Remove large files
git rm --cached Deep-Learning/Licence_Plate_Recognition/ocrmodel.h5
git rm --cached Deep-Learning/Main-Scripts/ocrmodel.h5
git rm --cached Deep-Learning/Licence_plate_detection/lapi.weights
git rm --cached "Deep-Learning/Licence_plate_detection/Attachments.zip"
git rm -r --cached "Deep-Learning/Licence_plate_detection/Attachments/"
git rm -r --cached Deep-Learning/output/
git rm -r --cached Deep-Learning/uploads/

# 3. Add .gitignore
git add .gitignore

# 4. Commit
git commit -m "Remove large files and add .gitignore"

# 5. Push
git push -u origin main
```

