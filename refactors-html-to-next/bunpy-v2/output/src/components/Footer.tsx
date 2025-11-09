import React from 'react';

/**
 * Props for the Footer component.
 * Currently, no specific props are defined, but this interface is included
 * for future extensibility and better type checking.
 */
interface FooterProps {
  // Add any props here if needed in the future, e.g., copyrightText: string;
}

/**
 * Renders the application's footer.
 * This component typically displays copyright information,
 * legal links, or other general site information.
 *
 * @param props - The props for the Footer component.
 */
const Footer: React.FC<FooterProps> = (props) => {
  // Basic inline styling for demonstration.
  // In a real application, consider using Tailwind CSS classes or a CSS module.
  const footerStyle: React.CSSProperties = {
    width: '100%',
    padding: '20px 0',
    backgroundColor: '#f8f8f8', // Light grey background
    textAlign: 'center',
    borderTop: '1px solid #e7e7e7', // Subtle top border
    marginTop: 'auto', // Pushes footer to the bottom if content is short
  };

  const currentYear = new Date().getFullYear();

  return (
    <footer style={footerStyle}>
      <p>&copy; {currentYear} MyCompany. All rights reserved.</p>
      {/* Add more footer content here if needed, e.g., links */}
      {/* <nav>
        <a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms of Service</a>
      </nav> */}
    </footer>
  );
};

export default Footer;