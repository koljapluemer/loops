# Firebase setup (do this yourself, in the console)

The proof-of-concept add-content-proposal flow (auth + proposals on the
public site, review in `local-cms/`) needs a few things set up in your
Firebase project (`the-platform-34609`) that code alone can't do. Nobody
here ran anything against your account — this is a checklist for you.

## 1. Enable Email/Password sign-in

Firebase console → **Authentication** → **Sign-in method** → enable
**Email/Password**.

## 2. Deploy the Firestore security rules

The rules are checked into the repo at `firestore.rules`. They let a
signed-in user create proposal documents (only their own, only with
`status: "pending"`) and read back their own proposals, but never update or
delete anything from the client — proposals only move to
accepted/rejected/deferred via `local-cms`, which uses an admin key that
bypasses these rules entirely.

Either:

- Firebase console → **Firestore Database** → **Rules** → paste in the
  contents of `firestore.rules` → **Publish**, or
- via the CLI (already installed here as `firebase`, v15.24+; `firebase.json`
  and `.firebaserc` are already checked in, pointing at `the-platform-34609`
  and `firestore.rules`):

  ```sh
  cd /home/brokkoli/GITHUB/the-platform   # firebase.json lives at repo root
  firebase login                          # interactive, opens a browser — run this yourself
  firebase deploy --only firestore:rules
  ```

  (Nobody ran `firebase login` or `firebase deploy` for you — those touch
  your account/project, so they're yours to run.)

No composite indexes are needed — `local-cms` only does single-field
equality queries on `status`.

## 3. Generate a service account key for `local-cms`

`local-cms` is the only piece that ever writes proposals into `data/` and
commits them — it needs admin access to Firestore to do that, separate from
the public site's client SDK config.

Firebase console → gear icon → **Project settings** → **Service accounts** →
**Generate new private key**. Save the downloaded JSON as:

```
local-cms/service-account.json
```

That path is already in `local-cms/.gitignore`, so it won't get committed.
(Alternatively, point the `FIREBASE_SERVICE_ACCOUNT` env var at wherever you
keep it.)

## 4. Install dependencies

```sh
cd static-site && npm install     # adds the firebase client SDK
cd ../local-cms && uv sync        # streamlit + firebase-admin
```

## 5. Run things

- Public site: `cd static-site && astro dev --background` (as usual).
- Review tool: `cd local-cms && uv run streamlit run app.py`, then open
  http://localhost:8501. See `local-cms/README.md`.

Nothing above was run for you — do these steps yourself when ready.
