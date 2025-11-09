```tsx
'use client';

import React from 'react';

interface PrimaryButtonProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  /**
   * The content to be rendered inside the button (e.g., text, icons).
   */
  children: React.ReactNode;
  /**
   * The URL the button navigates to.
   */
  href: string;
  /**
   * Optional key for language localization, if used in the application.
   */
  dataLangKey?: string;
  /**
   * Optional additional class names to apply to the button.
   * These will be combined with the default 'btn-primary' class.
   */
  className?: string;
}

/**
 * A primary call-to-action button component for navigation.
 * It renders an anchor tag styled as a primary button.
 */
const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  children,
  href,
  dataLangKey,
  className,
  ...rest // Captures any other standard HTMLAnchorElement attributes
}) => {
  // Combine the base 'btn-primary' class with any additional classes provided
  const combinedClassName = `btn-primary ${className || ''}`.trim();

  return (
    <a
      href={href}
      className={combinedClassName}
      data-lang-key={dataLangKey}
      {...rest} // Spread additional props like target, rel, etc.
    >
      {children}
    </a>
  );
};

export default PrimaryButton;
```