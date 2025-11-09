import React from 'react';
import Link from 'next/link';

/**
 * Represents a single navigation link.
 */
interface NavLink {
  /** The display text for the link. */
  label: string;
  /** The URL path for the link. */
  href: string;
  /** Optional: Indicates if the link is external. */
  external?: boolean;
}

/**
 * Props for the Navigation component.
 */
interface NavigationProps {
  /** An array of navigation links to display. */
  links: NavLink[];
  /** Optional: CSS class for the navigation container. */
  className?: string;
}

/**
 * A reusable navigation component for displaying a list of links.
 *
 * @param {NavigationProps} { links, className } - The properties for the component.
 * @returns {JSX.Element} The rendered navigation component.
 */
const Navigation: React.FC<NavigationProps> = ({ links, className }) => {
  if (!links || links.length === 0) {
    // Optionally render nothing or a placeholder if no links are provided
    // For robust applications, consider logging this case or providing a default message.
    console.warn("Navigation component rendered without any links.");
    return null;
  }

  return (
    <nav className={className}>
      <ul className="flex space-x-4">
        {links.map((link, index) => (
          <li key={link.href || `nav-item-${index}`}>
            {link.external ? (
              <a
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-700 hover:text-blue-600 transition-colors duration-200"
              >
                {link.label}
              </a>
            ) : (
              <Link href={link.href} passHref>
                <span className="text-gray-700 hover:text-blue-600 transition-colors duration-200 cursor-pointer">
                  {link.label}
                </span>
              </Link>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navigation;