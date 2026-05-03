# Next.js Port Guide

Welcome to the Next.js version of your Event Sponsor Marketplace MVP!

This guide is meant to help you transition from the mental model of **Python/Streamlit** into **JavaScript/React/Next.js**.

## 1. The Architecture Shift

### Streamlit: "Top-Down Execution"
In Streamlit (`app.py`), every time a user clicks a button or types in an input, the **entire Python script re-runs from top to bottom**. Data that needs to persist across these re-runs must be explicitly saved into `st.session_state`. 
It's incredibly fast to build, but it means the server is doing all the work, holding state in RAM.

### Next.js (React): "Component-Based State"
Next.js uses **React**. In React, the UI is broken down into modular pieces (Components). When a user clicks a button, only the specific Component that holds that piece of data (State) re-renders, while the rest of the page stays exactly as it is.
The heavy lifting is pushed to the user's browser, which is much more efficient.

## 2. State Management: `st.session_state` vs `useState`

In your Streamlit MVP, you used:
```python
# Streamlit
if "event" not in st.session_state:
    st.session_state.event = {"name": "Afro Vibes Night"}

# Updating state
st.session_state.event["name"] = "New Name"
```

In the Next.js app (`app/page.tsx`), we use the `useState` hook from React:
```tsx
// React
import { useState } from "react";

const [event, setEvent] = useState({ name: "Afro Vibes Night" });

// Updating state (we must replace the whole object)
setEvent({ ...event, name: "New Name" });
```
When `setEvent` is called, React knows exactly which parts of the UI depend on `event` and updates *only* those HTML elements instantly.

## 3. Developing Locally

To run this Next.js app locally:
1. Make sure you have Node.js installed on your machine.
2. In the project folder, open your terminal (PowerShell) and run:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:3000` in your browser. Any changes you make to `app/page.tsx` or `app/globals.css` will hot-reload instantly.

## 4. Deploying to Vercel (Free)

Vercel is the creator of Next.js and the absolute best place to host it. It is entirely free for side projects.

**Step 1: Push to GitHub**
Your code must be in a GitHub repository.
```bash
git add .
git commit -m "Initial Next.js Port"
git push origin main
```

**Step 2: Deploy**
1. Go to [vercel.com](https://vercel.com) and create an account using your GitHub.
2. Click **Add New... -> Project**.
3. Import the repository you just pushed to GitHub.
4. Leave all settings exactly as they are (Vercel automatically detects Next.js) and click **Deploy**.

Within 30 seconds, your app will be live on a global Edge network with a free SSL certificate and `.vercel.app` domain. Any future pushes to your GitHub `main` branch will automatically trigger a new deployment.

## Next Steps for the Future
This port currently mimics the "in-memory" state of the Streamlit MVP (refreshing the page resets the data). When you are ready to make it a "real" application, you will integrate **Supabase** directly into Next.js using the `@supabase/ssr` package. This will allow you to read and write directly to a real database from your frontend components safely and efficiently.
