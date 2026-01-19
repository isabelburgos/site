# Pre-Publish Security Checklist

Before running `mkdocs gh-deploy`:

## 1. Sync Public Content
```bash
python scripts/sync.py --verbose
```

Verify:
- ✅ Only public galleries are synced
- ✅ Attachments size is reasonable (< 100MB)
- ✅ No warnings about missing images

## 2. Build Locally
```bash
cd Website
mkdocs build --no-directory-urls
```

Verify:
- ✅ Build completes successfully
- ✅ No disk space errors
- ✅ Site size < 200MB

## 3. Security Scan
```bash
./verify-styles.sh  # Includes security checks
```

Verify:
- ✅ No Attachments leak warnings
- ✅ No private folders in site/
- ✅ Attachment count matches expectation

## 4. Manual Spot Check
```bash
python3 -m http.server 8000 --directory site &
# Visit http://localhost:8000
```

Check:
- Public galleries load correctly
- Images display
- No 404s in browser console
- No private content visible

## 5. Deploy
```bash
mkdocs gh-deploy
```

## Common Issues

**"Attachments size > 100MB"**
- Review which galleries are marked `public: true`
- Check for large images that should be compressed
- Verify no private galleries accidentally marked public

**"Referenced but not found" warnings**
- Gallery references image that doesn't exist
- Check spelling in markdown
- Verify attachment file exists in repo root

**Build fails with disk full**
- Clean old builds: `rm -rf site/`
- Check for symlink loops
- Verify Attachments isn't symlinked (should be copied files)
