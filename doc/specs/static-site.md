
## General

There are basically two experiences to the site:

- not authenticated: the site looks and feels like a classic static site, w/ pure static info about the apps etc. The user can freely browse. Apart from the option to sign in/up on top, they are generally not presented w/ forms they can't fill out etc. Ideally, js they don't need is not even loaded (if feasible)
- authenticated: now users can rate & propose new content

### Tech

- use latest tailwind+daisyui+lucide 
- only use custom CSS when really needed
- opt for short standard pattern whenever reasonably (e.g. a button should just have class `btn` unless special case)

- use clean, pattern driven ts architectures

- if authenticated: at the relevant places, the user should see THEIR proposals (e.g. proposed relationships, contexts, etc.) in a special color/style so they aren't confused and double propose. As in: the proposals that just live in the firestore for now! They should also be able to edit/delete those proposals. This should be cleanly represented in the firestore rules & setup also. Note also: this should work for input forms also.


### Style

- the site should give an impression of being crammed full of useful information. Craigslist, not BMW.
- keep whitespace sparse, do not use gradients, fades, glass morphism etc.

## Global/Reusable Components

### Header Bar

- on the left: name of site (for now "the platform"), linking to home
- on the right: auth stuff, depending on state: sign in+sign up, or link to "Profile"

### Node Forms

(node=anything represented by a single JSON file)

- nodes have a primary and a secondary type. Those are not free; they are represented by the folders in `data/`. 

## Pages

### Landing/Home

- brief intro about the site
- for now: a random order list of all `learn` content. Each should show up as clickable mini card, with a badge with the subtype (e.g. `able` or `know`) and then the (primary) name
- *if* authenticated: link at button to propose new learning node (links to page)

### Per Learning Node Site

- show the pixel art image next to the title
- show alternative names and tags
- show the outgoing relationships, grouped by contexts

*if authenticated:*

- below the context, show a button "propose additional context". Opens a popup modal form.
    - simple text input, but with a smart dropdown of existing context names from all over the app (this index needs to be built). However, the user may also input a new string not matching an existing entry.
- at the bottom of each context rel list: a button to propose a relationship (as in: a relationship within this context). Again, modal form. Should show the name of the page and the context the user is proposing for (not editable). Then, at top, should use a daisy tab layout: link to existing node, link to new node
    - to existing node: a plaintext input for the relationship label and dropdown for the target.
    - to new node: instead show two dropdowns for primary and secondary type, and the relevant inputs according to schema.


### Propose New Learning Node

- Simple form
- dropdown for learning secondary types
- text input for name