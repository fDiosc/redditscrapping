import React from 'react';

const SonarLogo = ({ size = 32, showText = true, hideText = false }) => {
    // Support both props for flexibility
    const displayText = showText && !hideText;

    return (
        <div className="flex items-center gap-3">
            <div className="relative">
                <div className="absolute inset-0 bg-indigo-500 rounded-full blur-md opacity-20 sonar-pulse"></div>
                <div className="absolute inset-0 bg-indigo-500 rounded-full blur-lg opacity-10 sonar-pulse-2"></div>
                <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative group-hover:scale-110 transition-transform duration-500">
                    <circle cx="16" cy="16" r="4" fill="#6366F1" />
                    <path d="M16 6C21.523 6 26 10.477 26 16C26 21.523 21.523 26 16 26"
                        stroke="#6366F1" strokeWidth="2.5" strokeLinecap="round" fill="none" className="sonar-pulse-mask" />
                    <path d="M6 16C6 10.477 10.477 6 16 6"
                        stroke="#6366F1" strokeWidth="1" strokeLinecap="round" fill="none" className="opacity-20" />
                </svg>
            </div>
            {displayText && (
                <h1 className={`${size > 30 ? 'text-2xl' : 'text-lg'} font-bold tracking-tight text-white font-display`}>
                    Sonar<span className="text-indigo-500">Pro</span>
                </h1>
            )}
        </div>
    );
};

export default SonarLogo;
