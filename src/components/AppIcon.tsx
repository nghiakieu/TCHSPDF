import React from 'react';

interface AppIconProps {
  size?: number;
  className?: string;
}

export const AppIcon: React.FC<AppIconProps> = ({ size = 20, className = '' }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      width={size}
      height={size}
      className={`shrink-0 ${className}`}
    >
      <defs>
        <filter id={`shadow-${size}`} x="-15%" y="-15%" width="130%" height="130%">
          <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" floodColor="#0F172A" floodOpacity="0.25" />
        </filter>
        <linearGradient id={`lensGlass-${size}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.95" />
          <stop offset="30%" stopColor="#E0F2FE" stopOpacity="0.85" />
          <stop offset="80%" stopColor="#BAE6FD" stopOpacity="0.75" />
          <stop offset="100%" stopColor="#93C5FD" stopOpacity="0.6" />
        </linearGradient>
        <linearGradient id={`handleGrad-${size}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FBBF24" />
          <stop offset="45%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#D97706" />
        </linearGradient>
        <linearGradient id={`foldFlap-${size}`} x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#FCA5A5" />
          <stop offset="100%" stopColor="#FECDD3" />
        </linearGradient>
      </defs>

      {/* Document group with subtle drop shadow */}
      <g filter={`url(#shadow-${size})`}>
        {/* White base paper layer */}
        <path
          d="M 10 57 L 50 57 C 52.8 57 55 54.8 55 52 L 55 16 L 43 4 L 14 4 C 11.2 4 9 6.2 9 9 L 9 52 C 9 55.3 11.7 58 15 58 L 50 58 C 53.3 58 56 55.3 56 52 L 56 16 Z"
          fill="#FFFFFF"
        />
        <rect x="9" y="8" width="46" height="51" rx="4.5" fill="#FFFFFF" />

        {/* Main Red PDF Document Body with cut top-right fold corner */}
        <path
          d="M 11 8 C 11 5.8 12.8 4 15 4 L 43.5 4 L 54 14.5 L 54 53 C 54 55.2 52.2 57 50 57 L 15 57 C 12.8 57 11 55.2 11 53 Z"
          fill="#EA4335"
        />

        {/* Fold shadow */}
        <path d="M 43.5 4 L 43.5 14.5 L 54 14.5 Z" fill="#B91C1C" opacity="0.22" />

        {/* Folded paper flap */}
        <path d="M 43.5 4 L 54 14.5 L 43.5 14.5 Z" fill={`url(#foldFlap-${size})`} />

        {/* PDF bold text */}
        <text
          x="16"
          y="27.5"
          fontFamily="'Segoe UI', -apple-system, Arial, sans-serif"
          fontSize="14.5"
          fontWeight="900"
          fill="#FFFFFF"
          letterSpacing="-0.6"
        >
          PDF
        </text>

        {/* Three pink/salmon document lines */}
        <rect x="16.5" y="33" width="18" height="3.5" rx="1.75" fill="#FCA5A5" />
        <rect x="16.5" y="39.5" width="18" height="3.5" rx="1.75" fill="#FCA5A5" />
        <rect x="16.5" y="46" width="12" height="3.5" rx="1.75" fill="#FCA5A5" />
      </g>

      {/* Magnifying Glass (Foreground) */}
      <g>
        {/* Golden-orange handle */}
        <path
          d="M 46.5 44.5 L 44.5 46.5 L 56 58 C 57.5 59.5 60 59.5 61.5 58 C 63 56.5 63 54 61.5 52.5 Z"
          fill={`url(#handleGrad-${size})`}
          stroke="#B45309"
          strokeWidth="0.8"
          strokeLinejoin="round"
        />

        {/* Handle highlight */}
        <line
          x1="47.5"
          y1="46.5"
          x2="58.5"
          y2="57.5"
          stroke="#FDE68A"
          strokeWidth="1"
          strokeLinecap="round"
          opacity="0.8"
        />

        {/* Dark blue connector ring */}
        <path d="M 45 43.5 L 43.5 45 L 47 48.5 L 48.5 47 Z" fill="#1E40AF" />

        {/* Circular blue lens frame */}
        <circle
          cx="38.5"
          cy="38.5"
          r="13.5"
          fill={`url(#lensGlass-${size})`}
          stroke="#2563EB"
          strokeWidth="3.4"
        />
        <circle
          cx="38.5"
          cy="38.5"
          r="11.8"
          fill="none"
          stroke="#60A5FA"
          strokeWidth="0.6"
          opacity="0.7"
        />

        {/* Curved glass glare highlight */}
        <path
          d="M 30 35 C 31 29.5 35.5 27 41.5 27 C 37 28 32.5 30.5 31.5 36 Z"
          fill="#FFFFFF"
          opacity="0.9"
        />
        <circle cx="32.5" cy="33" r="1.2" fill="#FFFFFF" opacity="0.9" />
      </g>
    </svg>
  );
};
