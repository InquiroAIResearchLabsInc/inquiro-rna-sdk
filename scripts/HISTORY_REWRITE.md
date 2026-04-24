# History rewrite (maintainers only)

To strip removed paths and scrub legacy token strings from **all** commits, use [git-filter-repo](https://github.com/newren/git-filter-repo) (not BFG). Do **not** commit a `--replace-text` rules file that contains the literal substrings you are purging, or those lines will be corrupted when the tool rewrites blobs.

1. Install: `pip install git-filter-repo`
2. Create a **temporary** rules file outside the repository (one line per literal `old==>new`).
3. From a **clean** working tree:

```bash
# Replace DIRECTORY with the internal-only tree you are removing (never commit a rules file that lists secret literals).
git filter-repo --path DIRECTORY/ --invert-paths --replace-text /path/outside/repo/replacements.txt --force
```

4. Re-add `origin` (`git remote add origin <url>`) and coordinate a **force-push** with all contributors.

After rewriting, run `git log --all -p | rg 'forbidden'` (or your org scanner) and confirm zero hits.
