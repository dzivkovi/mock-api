# Dual Remote Git Setup for Enterprise Email Compliance

## Timestamp and Context
- Date: 2025-07-09
- Context: Setting up dual Git remotes (GitHub + GitLab) for enterprise compliance
- Challenge: Siemens GitLab requires commits authored with company email addresses
- Goal: Enable seamless collaboration between personal GitHub and work GitLab repositories

## Question/Query
User needed to add GitLab as a second remote for team collaboration at Siemens while maintaining their existing GitHub repository. GitLab enterprise policies rejected commits authored with personal email addresses, requiring all commits to use Siemens company email format.

## Analysis and Findings

### Initial Problem
When attempting to push to GitLab, the enterprise server rejected commits:
```
remote: GitLab: Author 'Daniel.Zivkovic@gmail.com' is not a member of team
! [remote rejected] main -> main (pre-receive hook declined)
```

### Root Cause
Enterprise GitLab servers use pre-receive hooks to validate commit authorship. These hooks cannot be bypassed with `--force` flags as they validate at the server level before accepting any commits.

### Solution Strategy
Since the user worked as a contractor and couldn't get email whitelisting, the solution was to rewrite Git history to change all commit authors from personal to company email addresses.

### Implementation Steps

#### Step 1: Safety First
```bash
git branch backup-main  # Create backup before any history rewriting
```

#### Step 2: Add GitLab Remote
```bash
git remote add gitlab https://gitlab.industrysoftware.automation.siemens.com/daniel.zivkovic.ext/mock-api.git
```

#### Step 3: Rewrite Commit History
```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
if [ "$GIT_AUTHOR_EMAIL" = "Daniel.Zivkovic@gmail.com" ] || [ "$GIT_AUTHOR_EMAIL" = "daniel.zivkovic@gmail.com" ]
then
    export GIT_AUTHOR_EMAIL="daniel.zivkovic.ext@siemens.com"
    export GIT_AUTHOR_NAME="Daniel Z"
fi
if [ "$GIT_COMMITTER_EMAIL" = "Daniel.Zivkovic@gmail.com" ] || [ "$GIT_COMMITTER_EMAIL" = "daniel.zivkovic@gmail.com" ]
then
    export GIT_COMMITTER_EMAIL="daniel.zivkovic.ext@siemens.com"
    export GIT_COMMITTER_NAME="Daniel Z"
fi
' main
```

#### Step 4: Verify Changes
```bash
git log --format="%h %an <%ae>" | grep -i "gmail" | wc -l  # Should return 0
```

#### Step 5: Push to GitLab
```bash
git push gitlab main  # Now succeeds with company email addresses
```

#### Step 6: Sync GitHub
```bash
git push origin main --force  # Update GitHub with rewritten history
```

### Key Technical Considerations

#### Git Filter-Branch Behavior
- `git filter-branch` rewrites commit history by creating new commit objects
- Each rewritten commit gets a new SHA hash
- This causes the local branch to diverge from the original remote
- Force push is required to update remotes with rewritten history

#### Email Validation Patterns
Enterprise GitLab validated both author and committer email fields:
- `GIT_AUTHOR_EMAIL`: Person who originally wrote the code
- `GIT_COMMITTER_EMAIL`: Person who last applied the change

Both needed to be company email addresses for commits to be accepted.

#### Case Sensitivity Issues
The script handled multiple email formats found in the repository:
- `Daniel.Zivkovic@gmail.com` (capitalized)
- `daniel.zivkovic@gmail.com` (lowercase)

### Final Workflow

#### Dual Remote Configuration
```bash
git remote -v
# gitlab   https://gitlab.industrysoftware.automation.siemens.com/daniel.zivkovic.ext/mock-api.git (fetch)
# gitlab   https://gitlab.industrysoftware.automation.siemens.com/daniel.zivkovic.ext/mock-api.git (push)
# origin   https://github.com/dzivkovi/mock-api.git (fetch)
# origin   https://github.com/dzivkovi/mock-api.git (push)
```

#### Ongoing Development Workflow
```bash
# Normal development
git commit -m "feature: add new functionality"

# Push to both remotes
git push origin main      # GitHub (personal)
git push gitlab main      # GitLab (work)
```

### Alternative Approaches Considered

#### Option 1: Separate Clone (Not Chosen)
Create a separate repository clone for GitLab to avoid affecting the main repository. Rejected due to maintenance complexity.

#### Option 2: Manual Cherry-Picking (Not Chosen)
Manually cherry-pick commits with corrected authorship. Too tedious for 30+ commits.

#### Option 3: Enterprise Whitelisting (Not Available)
Request IT to whitelist personal email addresses. Not feasible for contractor status.

#### Option 4: Force Push Override (Not Possible)
Attempt to bypass server validation with force flags. Server-side hooks cannot be bypassed.

### Lessons Learned

#### Enterprise Git Policies
- Enterprise Git servers often have strict email validation
- Pre-receive hooks validate commits before acceptance
- Contractor accounts typically cannot get policy exceptions
- History rewriting is sometimes the only viable solution

#### Git History Management
- Always create backup branches before rewriting history
- `git filter-branch` is powerful but changes commit hashes
- Force push is required after history rewriting
- Both author and committer emails need to be updated

#### Dual Remote Strategy
- Dual remotes enable separation of personal and work repositories
- Single source of truth for work collaboration (GitLab)
- Personal backup and external collaboration (GitHub)
- Simplified team sharing through enterprise-compliant repository

### Best Practices for Future Projects

1. **Set up company email from project start** to avoid history rewriting
2. **Use conditional Git configuration** for different repositories:
   ```bash
   # .gitconfig
   [includeIf "gitdir:~/work/"]
       path = ~/work/.gitconfig-work
   ```
3. **Validate email requirements** before first commit to enterprise repositories
4. **Document dual remote setup** for team members
5. **Regular backup branches** before any history modifications

This solution successfully enabled dual remote collaboration while maintaining enterprise compliance requirements.