import React from 'react';

interface MainContentProps {
  /**
   * The content to be displayed within the main section.
   * This is typically the unique content for a specific page or view.
   */
  children: React.ReactNode;
  /**
   * Optional title for the main content area.
   * If provided, it will be rendered as an H1 heading at the top of the content.
   */
  title?: string;
  /**
   * Optional CSS class name for custom styling of the main container.
   * This allows for additional styling through Tailwind CSS classes or custom CSS modules.
   */
  className?: string;
}

/**
 * MainContent component serves as the primary container for a page's unique content.
 * It provides a flexible layout wrapper, typically centered with padding, and can
 * optionally display a title. It's designed to be used within a larger layout structure
 * (e.g., alongside a Header and Navigation component).
 *
 * Adheres to modern best practices including:
 * - Functional React component (`React.FC`).
 * - TypeScript type hints for props.
 * - Clean and readable code structure.
 * - Basic defensive rendering for optional props (e.g., `title`).
 * - Assumes a Tailwind CSS environment for common utility classes.
 */
const MainContent: React.FC<MainContentProps> = ({ children, title, className }) => {
  // Basic error handling / defensive rendering:
  // For a component primarily wrapping children, explicit error handling like try-catch
  // is typically not applied here but rather through React Error Boundaries
  // higher up the component tree. This component focuses on layout and presentation.
  // The rendering of 'children' directly handles cases where children might be null or undefined
  // by simply not rendering anything for them, which is often the desired behavior.

  return (
    <main className={`flex-grow container mx-auto px-4 py-8 ${className || ''}`}>
      {title && (
        <h1 className="text-3xl font-bold mb-6 text-gray-800">
          {title}
        </h1>
      )}
      <section className="bg-white p-6 rounded-lg shadow-md">
        {children}
      </section>
    </main>
  );
};

export default MainContent;