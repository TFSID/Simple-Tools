import React from 'react';
import Link from 'next/link';

interface HeaderProps {
  /** Optional title for the header, defaults to 'My Application' */
  title?: string;
  /** Optional array of navigation links */
  navLinks?: { href: string; label: string }[];
}

const defaultNavLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
  { href: '/contact', label: 'Contact' },
];

const Header: React.FC<HeaderProps> = ({
  title = 'My Application',
  navLinks = defaultNavLinks,
}) => {
  return (
    <header className="bg-gray-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold hover:text-gray-300 transition-colors duration-200">
          {title}
        </Link>
        <nav>
          <ul className="flex space-x-4">
            {navLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="hover:text-gray-300 transition-colors duration-200"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;