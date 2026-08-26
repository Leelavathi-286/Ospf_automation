# How to Initialize a Git Repo and Push to GitHub

This document records the exact step-by-step workflow used to initialize a local Git repository, commit files, create a remote GitHub repository, configure SSH, and push the code. Keep this as a template for future projects.

---

## Quick summary

- Initialize Git in your project folder
- Create .gitignore and README.md
- Stage and commit files
- Create GitHub repo and add it as remote
- Configure SSH keys and known_hosts
- Push the branch to GitHub

---

## Detailed step-by-step (commands to run, one at a time)

1. Open a terminal and change to your project directory

   cd /path/to/your/project

2. Check whether the directory is already a Git repo

   git status --short --branch

   If you see "fatal: not a git repository", run the next command.

3. Initialize a new Git repository

   git init

4. Create a .gitignore (starter template)

   cat > .gitignore <<'EOF'
   __pycache__/
   *.pyc
   .python-version
   .env
   .venv/
   env/
   .idea/
   .vscode/
   *.log
   *.pem
   *.key
   EOF

   Edit .gitignore as needed to include or exclude files (e.g., testbed.yaml, ospf_data.yaml).

5. Create a README

   echo "# my_project" > README.md

6. Configure Git identity (only needed once per machine)

   git config --global user.name "Your Full Name"
   git config --global user.email "your-email@example.com"

7. Stage files for commit

   git add .

8. Create initial commit

   git commit -m "Initial commit"

   If Git warns about author identity, re-run step 6 to set name/email and try committing again.

9. (Optional) If you previously had files in .gitignore but now want to track them:

   - Backup .gitignore
     cp .gitignore .gitignore.bak

   - Remove exact lines from .gitignore (safe approach):
     awk '!/^(filename1|filename2)$/' .gitignore > .gitignore.tmp && mv .gitignore.tmp .gitignore

   - Stage and commit the newly unignored files:
     git add . && git commit -m "Add previously ignored files"

10. Create a remote repository on GitHub

    - Open https://github.com/new
    - Repository name: choose a name (e.g., `my_project`)
    - Choose public or private
    - Click Create repository

11. Add the GitHub repository as the remote named `origin`

    - Using HTTPS:
      git remote add origin https://github.com/<your-username>/<repo>.git

    - Using SSH (preferred if you use SSH keys):
      git remote add origin git@github.com:<your-username>/<repo>.git

    Confirm remote:
      git remote -v

12. If using HTTPS, you may be prompted for username/password or a Personal Access Token (PAT). If push fails because prompts are disabled or credential helper not configured, consider switching to SSH.

13. Generate an SSH key (if you do not have one)

    ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519 -N ""

14. Add your public key to GitHub

    - Show the public key:
      cat ~/.ssh/id_ed25519.pub

    - Copy the single-line key output and go to GitHub → Settings → SSH and GPG keys → New SSH key → paste and save.

15. Add GitHub host keys to known_hosts (safe)

    ssh-keyscan -t rsa,ecdsa,ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null

16. Switch remote to SSH (if not already)

    git remote set-url origin git@github.com:<your-username>/<repo>.git
    git remote -v

17. Push your branch to GitHub and set upstream

    git push -u origin master

    (If your repository default branch is `main`, use `git push -u origin main` or rename local branch `git branch -M main`.)

18. Verify files on GitHub

    - Open https://github.com/<your-username>/<repo>

---

## How to push subsequent changes

- git add <file(s)>
- git commit -m "Describe the change"
- git push

---

## Troubleshooting / Common errors

- "fatal: not a git repository" → run `git init` in the project folder.
- "Author identity unknown" → set `git config --global user.name` and `git config --global user.email`.
- Files not staged because `.gitignore` contains them → remove those lines from `.gitignore` or use `git add -f <file>` (not recommended for secrets).
- HTTPS push fails due to disabled prompts → use SSH or create a PAT and use a credential helper.
- Host key verification failed → add GitHub's host key using `ssh-keyscan` or accept the prompt when asked.
- Accidentally committed secrets → do not push, remove from history using `git filter-repo` or BFG, rotate credentials, and ask for help.

---

## Best practices

- Never commit credentials or private keys. Use template files like `testbed.yaml.example` and add actual `testbed.yaml` to `.gitignore`.
- Use SSH for easier authentication on machines you control.
- Use meaningful commit messages and small commits.
- Add a LICENSE file for open source projects.
- Add CI (GitHub Actions) if you want tests to run on push/PR.

---

## Quick copy-paste commands (summary)

cd /path/to/project

# initialize
git init

# set identity (once)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# create files
echo "# project" > README.md
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.env
.venv/
EOF

# commit
git add .
git commit -m "Initial commit"

# add remote (SSH preferred)
git remote add origin git@github.com:<your-username>/<repo>.git

# push
git push -u origin master

---

If you want this document added to your repository (committed and pushed), I can do that for you. Otherwise, download it directly from your project folder: [GitHub_Push_Steps.md](/home/leelavathi/ospf_auto/GitHub_Push_Steps.md)
