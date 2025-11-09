```tsx
'use client';

import React from 'react';

// Define the type for a single social link
interface SocialLink {
  href: string;
  iconClass: string; // e.g., "fab fa-facebook-f"
  ariaLabel: string;
}

// Define props for the SocialIcons component
interface SocialIconsProps {
  /**
   * Defines the visual style and size of the social icons.
   * 'small' for a compact display (e.g., header).
   * 'large' for a prominent display (e.g., footer or dedicated section).
   * @default 'small'
   */
  variant?: 'small' | 'large';
  /**
   * An array of social media links to display.
   * If not provided, a default set of links will be used.
   */
  links?: SocialLink[];
}

// Default social media links based on the provided HTML
const defaultSocialLinks: SocialLink[] = [
  { href: '#', iconClass: 'fab fa-facebook-f', ariaLabel: 'Facebook' },
  { href: '#', iconClass: 'fab fa-instagram', ariaLabel: 'Instagram' },
  { href: '#', iconClass: 'fab fa-tiktok', ariaLabel: 'TikTok' },
  { href: '#', iconClass: 'fab fa-youtube', ariaLabel: 'YouTube' },
  { href: '#', iconClass: 'fab fa-discord', ariaLabel: 'Discord' },
];

/**
 * A client component to display a set of social media icons.
 * It can render different variants (small/large) and accepts custom links.
 * Requires Font Awesome 6.x to be linked globally (e.g., in layout.tsx or a global stylesheet).
 */
export const SocialIcons: React.FC<SocialIconsProps> = ({
  variant = 'small',
  links = defaultSocialLinks,
}) => {
  const containerClassName =
    variant === 'large' ? 'large-social-icons futura' : 'social-icons';

  return (
    <div className={containerClassName}>
      {links.map((link, index) => (
        <a
          key={index} // Using index as key is generally discouraged for dynamic lists, but acceptable for static lists like this.
          href={link.href}
          aria-label={link.ariaLabel}
          // Assuming `className` for `i` tag will apply Font Awesome styles
        >
          <i className={link.iconClass}></i>
        </a>
      ))}
    </div>
  );
};

export default SocialIcons;
```