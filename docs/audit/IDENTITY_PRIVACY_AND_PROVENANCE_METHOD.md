# Identity Privacy and GitHub Merge Provenance Method

## Control objective

Prevent personal identity metadata from entering public Git history without confusing privacy classification with proof of how a commit was created.

## Author and committer

A Git commit contains two identity roles. The **author** is the person represented as creating the change. The **committer** is the person or service that created the final commit object. A normal GitHub web merge can therefore have a human user-noreply author and GitHub's platform service as committer.

GitHub's generic platform service identity is non-personal because it represents shared GitHub infrastructure, not a person's contact channel. That does not make every identity from a GitHub-looking domain trustworthy.

## Offline privacy classification

`scripts/repository_audit.py` reads reachable history locally and permits only:

1. a user-specific GitHub noreply identity for a human author;
2. a user-specific GitHub noreply identity for a committer;
3. the exact GitHub generic platform service identity as committer, and only when the commit has exactly two parents; or
4. the one immutable, documented Stage 0 legacy exception.

The platform identity is rejected as an author. A single-parent platform commit is rejected. An arbitrary identity is rejected even if it uses the GitHub domain. Broad domain allowlisting would be unsafe because metadata strings are supplied by commit creators and can imitate a trusted-looking domain.

The offline result is deterministic but limited: parent count and metadata classification cannot prove the GitHub actor, signature, or pull-request association.

## Hosted provenance verification

`scripts/github_provenance_audit.py` identifies every reachable commit with the exact platform committer and obtains two narrowly used GitHub API responses. It requires all of the following:

- the API commit identifier matches local history;
- the committer actor is exactly `web-flow`;
- signature verification is true and its reason is valid;
- local and API metadata each show exactly two parents; and
- at least one associated pull request is closed, has a merge timestamp, and names the commit as its merge commit.

The check runs in a separate push-to-main CI job with `contents: read` and `pull-requests: read`. It does not run with those permissions against pull-request code. If the API is unavailable, authorization is insufficient, JSON is malformed, or evidence is incomplete, the check fails closed.

## Redaction behavior

The offline and hosted CLIs emit only fixed categories plus a file path or 12-character commit prefix. They never include the inspected identity, matched secret, API body, transport exception, or token. Tests construct synthetic prohibited values at runtime and assert that failures do not echo them. The sanitized PR #15 fixture contains actor, verification, parent, and pull-request fields only; it contains no address fields.

## Legacy history and rollback

The Stage 0 exception documents pre-existing metadata at one immutable commit. It is not a pattern and does not permit neighboring commits. Reverting a merge produces another commit and leaves the original merge reachable in published history, so reverting PR #15 would not erase its metadata. Rewriting or force-pushing public history is outside this control.

If this hotfix itself is defective, revert the focused hotfix PR and correct the policy in another reviewed change. Do not bypass the gate, broaden the identity rule, or add a commit-specific exception merely to make CI green.

## Limitations

The hosted check trusts GitHub's API association and signature report. It does not prove a contributor's civil identity, device security, account security, or intent. API availability is an operational dependency. The offline check remains useful without network access but makes no hosted-provenance claim.
