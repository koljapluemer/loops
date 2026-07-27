let's add a proof of concept for interactive add-content-proposals to the generated static site.

To the astro site, add firebase capabilities (I added a firestore and email+pw auth, here is the config object): 

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDrm9E2RspjT0Nkyr-v0XnemfjK4eA-kJA",
  authDomain: "the-platform-34609.firebaseapp.com",
  projectId: "the-platform-34609",
  storageBucket: "the-platform-34609.firebasestorage.app",
  messagingSenderId: "432957774499",
  appId: "1:432957774499:web:c8eea423fc80c59a4a3d16"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

build the usual infra around sign in, sign up, sign out, delete account.

signed in users can propose new objects (objects=anything representable as a json file), w/ a form to enter the core props

 for already existing objects (objects=anything represented as json file) authenticated users can also propose new relationships, with the relationship description and the proposed context description being plain text, and the object they have a relationship w/ chosen from a dropdown. this dropdown should be populated by a list of all existing objects; build this at ssg-build time. 

These proposals should be saved as temporary firebase objects.

In the local cms then, we should have a view (or views) to accept, reject or defer decision on these proposals, upon which they get integrated permanently into the JSON based, git-tracked storage.

Implement this minimally (proof of concept), but don't go for silly hacks, either. yes, the data base is CURRENTLY SMALL, but is in fact expected to grow.
If I need to do stuff in firebase, TELL ME or write doc TELLING ME what to do. Do not run server or try to fuck around in my accounts.
