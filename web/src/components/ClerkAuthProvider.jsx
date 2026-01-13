import React from 'react';
import { ClerkProvider } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!CLERK_PUBLISHABLE_KEY) {
    console.warn("Missing Clerk Publishable Key. Auth will not work.");
}

export const ClerkAuthProvider = ({ children }) => {
    if (!CLERK_PUBLISHABLE_KEY) {
        return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-red-400 p-8 text-center font-mono">
            Missing VITE_CLERK_PUBLISHABLE_KEY in web/.env
        </div>;
    }

    return (
        <ClerkProvider
            publishableKey={CLERK_PUBLISHABLE_KEY}
            afterSignOutUrl="/"
        >
            {children}
        </ClerkProvider>
    );
};
