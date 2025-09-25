import csv
import os
from collections import defaultdict
from git import Repo

repo = Repo(os.getcwd())
main_branch = "main"  # Adjust if your main branch name is different

author_commits = defaultdict(int)
author_lines = defaultdict(int)
author_prefixes = defaultdict(lambda: {'frontend/': 0, 'backend/': 0, 'testing/': 0})
author_filetypes = defaultdict(lambda: defaultdict(int))
author_files = defaultdict(set)

EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

for commit in repo.iter_commits(main_branch, no_merges=True):
    author = commit.author.name
    author_commits[author] += 1

    msg = commit.message.lower()
    for prefix in ['frontend/', 'backend/', 'testing/']:
        if msg.startswith(prefix):
            author_prefixes[author][prefix] += 1

    # Handle stats
    if commit.parents:
        stats = commit.stats
        author_lines[author] += stats.total['insertions'] + stats.total['deletions']
        for filepath in stats.files:
            ext = os.path.splitext(filepath)[1] or 'NO_EXT'
            author_filetypes[author][ext] += 1
            author_files[author].add(filepath)
    else:
        # Initial commit: diff against empty tree
        stats_raw = repo.git.diff('--numstat', EMPTY_TREE, commit.hexsha)
        lines = stats_raw.strip().split('\n')
        insertions = deletions = 0
        for line in lines:
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                ins, dels, path = parts
                try:
                    insertions += int(ins)
                except ValueError:
                    pass
                try:
                    deletions += int(dels)
                except ValueError:
                    pass
                ext = os.path.splitext(path)[1] or 'NO_EXT'
                author_filetypes[author][ext] += 1
                author_files[author].add(path)
        author_lines[author] += insertions + deletions

os.makedirs('stats', exist_ok=True)

# 1. author_commit_stats.csv
with open('stats/author_commit_stats.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Author', 'Commits', 'Lines Changed'])
    for author in author_commits:
        writer.writerow([author, author_commits[author], author_lines[author]])

# 2. author_commit_prefixes.csv
with open('stats/author_commit_prefixes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Author', 'frontend/', 'backend/', 'testing/'])
    for author in author_prefixes:
        p = author_prefixes[author]
        writer.writerow([author, p['frontend/'], p['backend/'], p['testing/']])

# 3. author_filetypes.csv
filetypes = set()
for d in author_filetypes.values():
    filetypes.update(d.keys())
filetypes = sorted(filetypes)
with open('stats/author_filetypes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Author'] + filetypes)
    for author in author_filetypes:
        row = [author] + [author_filetypes[author].get(ft, 0) for ft in filetypes]
        writer.writerow(row)

# 4. author_files_modified.csv (flat, semicolon separated)
with open('stats/author_files_modified.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Author', 'Files Modified'])
    for author in author_files:
        files = sorted(author_files[author])
        writer.writerow([author, '; '.join(files)])

# 5. author_files_modified_tree.csv (tree format, indented via columns)
def build_tree(paths):
    tree = {}
    for path in paths:
        parts = path.split(os.sep)
        d = tree
        for part in parts:
            d = d.setdefault(part, {})
    return tree

def tree_to_csv_rows(tree, prefix=None):
    if prefix is None:
        prefix = []
    rows = []
    for name, subtree in sorted(tree.items()):
        row = [''] * len(prefix) + [name]
        rows.append(row)
        if subtree:
            rows.extend(tree_to_csv_rows(subtree, prefix + [name]))
    return rows

MAX_DEPTH = 10  # increase if you have deeper folders

with open('stats/author_files_modified_tree.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['Author'] + [f'Level {i}' for i in range(1, MAX_DEPTH+1)]
    writer.writerow(header)
    for author in author_files:
        files = sorted(author_files[author])
        tree = build_tree(files)
        rows = tree_to_csv_rows(tree)
        first = True
        for row in rows:
            # Pad row to max depth
            row += [''] * (MAX_DEPTH - len(row))
            if first:
                writer.writerow([author] + row)
                first = False
            else:
                writer.writerow([''] + row)
