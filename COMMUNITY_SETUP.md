# Community Chat & Inbox — Firebase setup

`community.html` provides a **public chat room** and a **private inbox (DMs)**. It runs on a free
Firebase project (Firestore + Google sign-in). The Firebase web config is **not secret** — access is
controlled entirely by the Firestore security rules below.

## 1. Create the project (5 min)
1. Go to https://console.firebase.google.com/ → **Add project** (name it e.g. `red-team-tracker`). Google
   Analytics is optional — skip it.
2. **Build → Authentication → Get started → Sign-in method → Google → Enable → Save.**
3. **Build → Firestore Database → Create database → Production mode → pick a region → Enable.**

## 2. Get the web config
1. **Project settings (gear) → General → Your apps → Web (`</>`) → register app** (nickname anything;
   skip Hosting).
2. Copy the `firebaseConfig` object it shows you (apiKey, authDomain, projectId, appId, …).
3. Paste it into `community.html`, replacing the `firebaseConfig` block near the top of the `<script>`.
   (Or send it to me and I'll paste + redeploy.)

## 3. Authorize your domains
**Authentication → Settings → Authorized domains → Add domain** and add:
- `azizbinmohammad.github.io`  (the live site)
- `localhost`  (for local testing)

Without this, Google sign-in popups are rejected.

## 4. Paste the security rules
**Firestore Database → Rules**, replace everything with this, then **Publish**:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Public profiles: any signed-in user can read; you may only write your own.
    match /users/{uid} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == uid;
    }

    // Public chat: signed-in users read all; create your own messages (1..1000 chars); no edits/deletes.
    match /chat/{msg} {
      allow read: if request.auth != null;
      allow create: if request.auth != null
        && request.resource.data.uid == request.auth.uid
        && request.resource.data.text is string
        && request.resource.data.text.size() > 0
        && request.resource.data.text.size() <= 1000;
      allow update, delete: if false;
    }

    // Private DM threads: only the two participants can read or write.
    match /threads/{cid} {
      allow read:   if request.auth != null && request.auth.uid in resource.data.participants;
      allow create: if request.auth != null && request.auth.uid in request.resource.data.participants;
      allow update: if request.auth != null && request.auth.uid in resource.data.participants;
      allow delete: if false;

      match /messages/{m} {
        allow read: if request.auth != null
          && request.auth.uid in get(/databases/$(database)/documents/threads/$(cid)).data.participants;
        allow create: if request.auth != null
          && request.resource.data.from == request.auth.uid
          && request.auth.uid in get(/databases/$(database)/documents/threads/$(cid)).data.participants
          && request.resource.data.text is string
          && request.resource.data.text.size() > 0
          && request.resource.data.text.size() <= 2000;
        allow update, delete: if false;
      }
    }
  }
}
```

## 5. Create the one composite index the inbox needs
The "your conversations" list queries `threads` by `participants` (array-contains) ordered by `lastTs`.
The first time it runs, the browser console prints a **"The query requires an index"** link — click it and
**Create index** (takes ~1 min). Or pre-create it: **Firestore → Indexes → Composite → Add index**,
collection `threads`, fields: `participants` (Array-contains) + `lastTs` (Descending).

## Done
Reload `https://azizbinmohammad.github.io/red-team-tracker/community.html`, sign in with Google, and the
public chat + inbox are live. Free-tier limits (50k reads/day, 20k writes/day) are ample for a community
this size.

### Notes / moderation
- Public chat messages are visible to every signed-in user; inbox messages are private to the two people in
  the thread (enforced by the rules above — not just the UI).
- Messages are capped (1000 chars chat / 2000 DM) and can't be edited or deleted by clients. To remove an
  abusive message or user, delete it in the Firestore console. For heavier abuse, you can add App Check or a
  Cloud Function later.
