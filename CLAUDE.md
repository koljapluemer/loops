A page collecting how to learn stuff.

## Architecture 

- source of truth: json folder/file structure in `data/`
- can be publically viewed via the astro site in `static-site`
- authenticated users (firebase auth) can make proposals temporarily stored in a firestore, also via the astro site
- content is then accepted/rejected in the local admin cms (`local-cms`), powered by uv+streamlit

## Guidelines

- this is currently a young site, but bound to grow. Architect with much larger data volume in mind.
- yet, this page's aim is to be as low-tech and pragmatic as possible.
- follow best practices per used technology, but do not LARP as big tech doing the next Facebook.