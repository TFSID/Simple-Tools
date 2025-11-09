```tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';

/**
 * Props for the DarkModeToggle component.
 * Currently, no external props are needed, but an interface is provided for future extensibility.
 */
interface DarkModeToggleProps {}

/**
 * DarkModeToggle is a client component that provides a user interface to
 * switch between dark and light modes. It persists the user's preference
 * in localStorage and applies the 'dark-mode' class to the document body.
 *
 * It also handles the initial load by checking localStorage to prevent a flash
 * of unstyled content (FOUC) by applying the mode class as early as possible on the client.
 */
const DarkModeToggle: React.FC<DarkModeToggleProps> = () => {
  // State to manage the current dark mode status.
  // Initialized to 'false' (light mode) and then hydrated from localStorage.
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  /**
   * Effect hook to synchronize the dark mode state with localStorage and document.body class.
   * This effect runs once on component mount to initialize the state from localStorage.
   *
   * Note: The original HTML had an inline script to prevent FOUC *before* the body rendered.
   * For React client components, the initial render will occur, and then `useEffect` runs.
   * To replicate the FOUC prevention strictly, an inline script tag in `app/layout.tsx` or
   * `pages/_document.tsx` is generally the recommended approach for Next.js.
   * This component handles setting the `dark-mode` class on the `body` once it mounts.
   */
  useEffect(() => {
    try {
      // Attempt to retrieve saved preference from localStorage
      const savedMode = localStorage.getItem('aquanimeDarkMode');
      const initialDarkMode = savedMode === 'true'; // Convert string to boolean

      // Update the component's state
      setIsDarkMode(initialDarkMode);

      // Apply the initial class to the document body
      if (initialDarkMode) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }
    } catch (error) {
      console.error('Failed to access localStorage for dark mode:', error);
      // Fallback gracefully if localStorage is not available or throws an error (e.g., security settings)
    }
  }, []); // Empty dependency array ensures this effect runs only once on mount

  /**
   * Effect hook to update the document.body class and localStorage
   * whenever the `isDarkMode` state changes.
   */
  useEffect(() => {
    try {
      if (isDarkMode) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('aquanimeDarkMode', 'true');
      } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('aquanimeDarkMode', 'false');
      }
    } catch (error) {
      console.error('Failed to update localStorage or body class:', error);
    }
  }, [isDarkMode]); // Reruns whenever isDarkMode state changes

  /**
   * Callback function to toggle the dark mode state.
   * This function is memoized using useCallback to prevent unnecessary re-renders.
   */
  const toggleDarkMode = useCallback(() => {
    setIsDarkMode(prevMode => !prevMode);
  }, []); // No dependencies as it only toggles its own state

  return (
    <div className="dark-mode-toggle" onClick={toggleDarkMode} role="button" aria-label={`Toggle to ${isDarkMode ? 'light mode' : 'dark mode'}`}>
      {/* Icon dynamically changes based on current mode */}
      <i className={`fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}`}></i>
      {/* Text dynamically changes based on current mode */}
      <span>{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
    </div>
  );
};

export default DarkModeToggle;
```