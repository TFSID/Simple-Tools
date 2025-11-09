```typescript
'use client';

import React from 'react';

interface SecondaryButtonProps {
  /** The URL to navigate to when the button is clicked. */
  href: string;
  /** The content to be rendered inside the button (e.g., text, icons). */
  children: React.ReactNode;
  /** Optional click event handler. */
  onClick?: (event: React.MouseEvent<HTMLAnchorElement>) => void;
  /** Optional additional CSS classes to apply to the button. */
  className?: string;
  /** Optional target attribute for the anchor tag (e.g., '_blank'). */
  target?: string;
  /** Optional rel attribute for the anchor tag (e.g., 'noopener noreferrer'). */
  rel?: string;
  /** Optional data-lang-key attribute for localization. */
  'data-lang-key'?: string;
}

/**
 * A reusable Next.js client component for a secondary style button.
 * It's styled with a Tailwind CSS approximation of a common secondary button design
 * (outlined, colored text, hover effect) and includes the 'poppins' font class.
 */
export default function SecondaryButton({
  href,
  children,
  onClick,
  className = '',
  target,
  rel,
  'data-lang-key': dataLangKey,
}: SecondaryButtonProps) {
  // Base Tailwind CSS classes for a secondary button.
  // This is an interpretation of "btn-secondary" using common design patterns,
  // as the original CSS is not provided. It assumes an outlined style.
  // The 'poppins' class is included as it appears frequently in the original HTML.
  const baseClasses = `
    inline-flex items-center justify-center
    px-6 py-3
    border-2 border-current rounded-full
    text-indigo-600
    font-medium text-base
    hover:bg-indigo-600 hover:text-white
    focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
    transition-colors duration-300 ease-in-out
    whitespace-nowrap
    poppins
  `.trim().replace(/\s+/g, ' '); // Clean up extra whitespace

  // Combine base classes with any additional classes provided via props.
  const mergedClasses = `${baseClasses} ${className}`.trim();

  return (
    <a
      href={href}
      className={mergedClasses}
      onClick={onClick}
      target={target}
      rel={rel}
      data-lang-key={dataLangKey}
    >
      {children}
    </a>
  );
}
```