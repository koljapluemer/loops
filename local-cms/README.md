# local-cms

Local-only review tool for proposals (new objects / new relationships)
submitted by signed-in users on the public site. Never deployed: it talks to
Firestore with an admin service-account key that bypasses `firestore.rules`,
and it writes directly into `../data/` and commits with `git`.

See `../FIREBASE_SETUP.md` for the one-time Firebase console steps and for
where to put the service account key.

## Run

```sh
cd local-cms
uv run streamlit run app.py
```

Opens at http://localhost:8501. Three tabs: pending / accepted / rejected /
deferred proposals.

- **Accept** writes the proposal into `data/` (as a new JSON file for an
  object proposal, or merged into the source object's `contexts` for a
  relationship proposal) and creates a git commit in this repo. Nothing is
  pushed.
- **Reject** / **Defer** just update the proposal's status in Firestore.
- Accepting fails loudly (and leaves the proposal `pending`) if, e.g., the
  target file already exists — resolve the conflict by hand and retry.
