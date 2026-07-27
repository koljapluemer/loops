import { initializeApp } from "firebase/app";
import {
  getAuth,
  onAuthStateChanged,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  deleteUser,
  reauthenticateWithCredential,
  EmailAuthProvider,
  type User,
} from "firebase/auth";
import {
  initializeFirestore,
  collection,
  addDoc,
  serverTimestamp,
} from "firebase/firestore";

// These identifiers are safe to ship in client code: Firebase access is
// governed by Firestore/Auth security rules, not by keeping this config
// secret. See ../../../FIREBASE_SETUP.md for the rules that must be in
// place in the Firebase console for this to be safe.
const firebaseConfig = {
  apiKey: "AIzaSyDrm9E2RspjT0Nkyr-v0XnemfjK4eA-kJA",
  authDomain: "the-platform-34609.firebaseapp.com",
  projectId: "the-platform-34609",
  storageBucket: "the-platform-34609.firebasestorage.app",
  messagingSenderId: "432957774499",
  appId: "1:432957774499:web:c8eea423fc80c59a4a3d16",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
// Optional proposal fields (description, sub, topics, url…) are passed as
// `undefined` when left blank; Firestore's SDK rejects `undefined` field
// values unless told to drop them.
export const db = initializeFirestore(app, { ignoreUndefinedProperties: true });

export function onAuth(cb: (user: User | null) => void): () => void {
  return onAuthStateChanged(auth, cb);
}

export async function signUp(email: string, password: string): Promise<void> {
  await createUserWithEmailAndPassword(auth, email, password);
}

export async function signIn(email: string, password: string): Promise<void> {
  await signInWithEmailAndPassword(auth, email, password);
}

export async function signOutUser(): Promise<void> {
  await signOut(auth);
}

// Firebase requires a "recent" login to delete an account. If no password
// is supplied and the session turns out to be stale, the original
// auth/requires-recent-login error is rethrown so the caller can prompt for
// a password and retry with it.
export async function deleteAccount(password?: string): Promise<void> {
  const user = auth.currentUser;
  if (!user || !user.email) throw new Error("not signed in");
  try {
    await deleteUser(user);
  } catch (err: any) {
    if (err?.code === "auth/requires-recent-login" && password) {
      const credential = EmailAuthProvider.credential(user.email, password);
      await reauthenticateWithCredential(user, credential);
      await deleteUser(user);
    } else {
      throw err;
    }
  }
}

export interface ObjectProposalInput {
  top: string;
  sub?: string;
  slug: string;
  name: string;
  description?: string;
  topics?: string[];
  url?: string;
  urlLabel?: string;
}

export interface RelationshipProposalInput {
  sourceId: string;
  sourceName: string;
  targetId: string;
  targetName: string;
  context: string;
  label: string;
}

function requireUser(): User {
  const user = auth.currentUser;
  if (!user) throw new Error("not signed in");
  return user;
}

export async function submitObjectProposal(
  input: ObjectProposalInput,
): Promise<void> {
  const user = requireUser();
  await addDoc(collection(db, "proposals"), {
    type: "object",
    status: "pending",
    createdAt: serverTimestamp(),
    submittedByUid: user.uid,
    submittedByEmail: user.email,
    ...input,
  });
}

export async function submitRelationshipProposal(
  input: RelationshipProposalInput,
): Promise<void> {
  const user = requireUser();
  await addDoc(collection(db, "proposals"), {
    type: "relationship",
    status: "pending",
    createdAt: serverTimestamp(),
    submittedByUid: user.uid,
    submittedByEmail: user.email,
    ...input,
  });
}
