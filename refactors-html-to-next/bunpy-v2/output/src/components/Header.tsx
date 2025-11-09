import React from 'react';

/**
 * Props for the Header component.
 * Currently, no specific props are defined, but this interface is included
 * for future extensibility and type safety.
 */
interface HeaderProps {
  // You can define props here, e.g., title: string; navLinks: { label: string; href: string; }[];
}

/**
 * A responsive Header component for the application.
 * It typically includes the site title/logo and navigation links.
 */
const Header: React.FC<HeaderProps> = () => {
  return (
    <header className="bg-gray-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        {/* Site Title or Logo */}
        <div className="flex items-center">
          <a href="/" className="text-2xl font-bold text-white hover:text-gray-300 transition-colors duration-200">
            My App
          </a>
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex space-x-4">
          <a href="/" className="text-white hover:text-gray-300 transition-colors duration-200">Home</a>
          <a href="/about" className="text-white hover:text-gray-300 transition-colors duration-200">About</a>
          <a href="/services" className="text-white hover:text-gray-300 transition-colors duration-200">Services</a>
          <a href="/contact" className="text-white hover:text-gray-300 transition-colors duration-200">Contact</a>
        </nav>

        {/* Mobile Menu Button (Hamburger Icon) - Hidden on desktop */}
        <div className="md:hidden">
          <button
            aria-label="Toggle Navigation Menu"
            className="text-white focus:outline-none focus:ring-2 focus:ring-white p-2 rounded-md"
            // You'd typically add state for opening/closing mobile menu here
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path>
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Navigation (Hidden by default, shown when menu button is clicked) */}
      {/* This would typically be conditionally rendered based on a state variable */}
      {/* <div className="md:hidden mt-2">
        <nav className="flex flex-col space-y-2 px-4 py-2 bg-gray-700">
          <a href="/" className="text-white hover:text-gray-300">Home</a>
          <a href="/about" className="text-white hover:text-gray-300">About</a>
          <a href="/services" className="text-white hover:text-gray-300">Services</a>
          <a href="/contact" className="text-white hover:text-gray-300">Contact</a>
        </nav>
      </div> */}
    </header>
  );
};

export default Header;