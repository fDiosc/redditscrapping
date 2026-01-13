# SonarPro Testing Guide 🚀

This guide outlines the steps to verify the new **SonarPro** branding, landing page, and authentication flow.

## 1. Prerequisites
Before testing, ensure you have set up your **Clerk Publishable Key**:
1. Open `web/.env`.
2. Replace `pk_test_placeholder` with your real key from the [Clerk Dashboard](https://dashboard.clerk.com/).
3. Save the file.

---

## 2. Starting the Environment
Run both the backend and frontend in separate terminals:

**Backend (API):**
```powershell
radar serve
```

**Frontend (Web):**
```powershell
cd web
npm run dev
```
> [!IMPORTANT]
> **Check the Port!** Look at the terminal output. If you see `Port 5173 is in use, trying another one...`, you must use the new URL (e.g., `http://localhost:5174/`). Accessing the wrong port will show a blank screen.

---

## 3. Testing the Landing Page
1.  **Open the Browser**: Navigate to the URL provided by Vite.
2.  **Verify Branding**: You should see the **SonarPro** logo with the animated sonar pulse.
3.  **Check Typography**: Confirm the use of `Outfit` (Headlines) and `DM Sans` (Body).
4.  **Explore Sections**:
    *   **Hero**: Check the "Find your customers on Reddit" message and the CTA animation.
    *   **The Engines**: Hover over "Detect", "Analyze", and "Respond" to see the feature details.
    *   **Pricing**: Verify the four tiers (Free, Starter, Pro, Team).

---

## 4. Testing the Login Flow
1.  **Click "Sign In" or "Get Started"**: On the landing page.
2.  **Clerk Modal**: A Clerk authentication modal should appear.
3.  **Sign Up/In**: Use a test email or social provider.
4.  **Redirection**: After successful login, you should be automatically redirected to the **SonarPro Dashboard**.

---

## 5. Testing the Dashboard (Protected App)
1.  **Visual Audit**: Confirm the dashboard now uses the Indigo theme and SonarPro branding in the sidebar.
2.  **Stat Cards**: Click on "High Intensity" or "High Fit Leads" to verify the interactive filtering and sorting.
3.  **AI Insights**: Expand a thread and verify the new "targeted" fields:
    *   `u/username` (Author/Commenter badge).
    *   Pain point summary and quotes.
4.  **User Management**: Click the user avatar in the bottom-left of the sidebar to test the **Clerk User Profile** and **Sign Out** functionality.

---

## 6. Verification Checklist
- [ ] Landing page renders without errors.
- [ ] Sonar pulse animation is active.
- [ ] Sign-in button opens Clerk modal.
- [ ] Dashboard is inaccessible without login (try navigating directly).
- [ ] Stat cards filter the thread list correctly.
- [ ] Sign-out returns you to the landing page.

---
**Happy Testing!** If you encounter any issues, let me know.
