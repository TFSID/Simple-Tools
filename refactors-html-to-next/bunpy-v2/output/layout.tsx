import './globals.css';

import type { Metadata } from 'next';

// Assuming Header and Footer components are located in src/components
// The path is relative from src/app to src/components
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';

/**
 * Metadata for the entire application.
 * This object defines properties like title, description, and other SEO-related tags
 * that will be applied to the <head> of the HTML document.
 */
export const metadata: Metadata = {
  title: 'Next.js Application', // Default title for the application
  description: 'A modern web application built with Next.js with a focus on user experience.', // Default description
  // Potentially add more metadata here, such as:
  // viewport: 'width=device-width, initial-scale=1',
  // icons: {
  //   icon: '/favicon.ico',
  // },
  // Open Graph / Social Media metadata (e.g., og:title, og:description, og:image)
  // metadataBase: new URL('https://yourdomain.com'), // Important for absolute URLs in production
};

/**
 * RootLayout component that defines the basic HTML structure for the entire application.
 * It wraps all pages and ensures global styles and metadata are applied.
 * This layout includes a global Header and Footer component that will appear on every page,
 * wrapping the main content (`children`).
 *
 * @param {Readonly<{ children: React.ReactNode }>} props - React props containing children elements.
 *                                                         'children' represents the content of the current page
 *                                                         or nested layouts.
 * @returns {JSX.Element} The root HTML structure including the head, body, global header, main content area, and global footer.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en"> {/* Defines the document's language for better accessibility and SEO */}
      <body>
        {/* Render the global Header component, which will be present on all pages */}
        <Header />

        {/*
          The <main> element semantically represents the dominant content of the <body>.
          'children' will be rendered inside this <main> tag, containing the specific page content.
        */}
        <main>
          {children}
        </main>

        {/* Render the global Footer component, which will be present on all pages */}
        <Footer />
      </body>
    </html>
  );
}