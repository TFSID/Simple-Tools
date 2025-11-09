```typescript
'use client';

import React, { useState, useEffect } from 'react';

/**
 * Props for the LangModeToggles component.
 * Currently, no external props are required as state is managed internally.
 */
interface LangModeTogglesProps {
  // You might extend this to accept an initial mode or language from parent components if needed,
  // e.g., `initialDarkMode?: boolean; initialLanguage?: string;`
}

/**
 * A client component that provides toggles for dark mode and language.
 * It manages the state of dark mode and language preference using localStorage
 * and updates the document's body class and html lang attribute accordingly.
 */
const LangModeToggles: React.FC<LangModeTogglesProps> = () => {
  // State for dark mode: `true` if dark mode is active, `false` otherwise.
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  // State for language: 'id' for Indonesian, 'en' for English.
  const [lang, setLang] = useState<string>('id');

  // Effect to initialize dark mode state from localStorage or system preference on component mount.
  // This also handles removing the 'dark-mode-preload' class potentially added by an inline script.
  useEffect(() => {
    // Check localStorage for a saved dark mode preference.
    const savedDarkMode = localStorage.getItem('aquanimeDarkMode');
    // Check user's system preference for dark mode.
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Determine the initial dark mode state:
    // 1. If a preference is saved in localStorage, use that.
    // 2. Otherwise, use the system's dark mode preference.
    const initialDarkMode = savedDarkMode !== null ? savedDarkMode === 'true' : prefersDark;
    setIsDarkMode(initialDarkMode); // Update the component's state.

    // Remove the 'dark-mode-preload' class which might have been added by an inline script
    // to prevent FOUC (Flash Of Unthemed Content) before React hydrates.
    document.documentElement.classList.remove('dark-mode-preload');
  }, []); // Empty dependency array means this effect runs only once after the initial render.

  // Effect to apply/remove the 'dark-mode' class to `document.body`
  // and update `localStorage` whenever `isDarkMode` state changes.
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('aquanimeDarkMode', 'true');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('aquanimeDarkMode', 'false');
    }
  }, [isDarkMode]); // This effect runs whenever the `isDarkMode` state changes.

  // Effect to initialize language state from localStorage on component mount.
  useEffect(() => {
    // Check localStorage for a saved language preference.
    const savedLang = localStorage.getItem('aquanimeLang');
    if (savedLang) {
      setLang(savedLang); // Use the saved preference.
    } else {
      // If no saved language, use the document's current lang attribute, default to 'id'.
      setLang(document.documentElement.lang || 'id');
    }
  }, []); // Empty dependency array means this effect runs only once after the initial render.

  // Effect to update the `document.documentElement.lang` attribute
  // and `localStorage` whenever the `lang` state changes.
  useEffect(() => {
    document.documentElement.lang = lang;
    localStorage.setItem('aquanimeLang', lang);
  }, [lang]); // This effect runs whenever the `lang` state changes.

  /**
   * Toggles the dark mode state between `true` and `false`.
   */
  const toggleDarkMode = () => {
    setIsDarkMode((prevMode) => !prevMode);
  };

  /**
   * Toggles the language state between 'id' (Indonesian) and 'en' (English).
   */
  const toggleLanguage = () => {
    setLang((prevLang) => (prevLang === 'id' ? 'en' : 'id'));
  };

  return (
    <div className="lang-mode-toggles poppins">
      {/* Dark Mode Toggle */}
      <div
        className="dark-mode-toggle"
        id="dark-mode-toggle" // Retaining original ID for consistency, though often unnecessary in React.
        onClick={toggleDarkMode} // Attach event handler to toggle dark mode.
        role="button" // Improve accessibility by indicating it's a clickable element.
        tabIndex={0} // Make the element focusable for keyboard navigation.
        aria-label={isDarkMode ? 'Toggle Light Mode' : 'Toggle Dark Mode'} // Provide a descriptive label for screen readers.
      >
        {/* Font Awesome icon changes based on dark mode state (moon for dark, sun for light). */}
        <i className={`fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}`}></i>{' '}
        {/* Text label changes based on dark mode state. */}
        <span>{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
      </div>

      {/* Language Toggle (added based on component name "LangModeToggles") */}
      <div
        className="language-toggle" // A class for styling the language toggle.
        onClick={toggleLanguage} // Attach event handler to toggle language.
        role="button"
        tabIndex={0}
        aria-label={`Switch to ${lang === 'id' ? 'English' : 'Indonesian'}`}
      >
        {/* Display current language in uppercase, e.g., "ID" or "EN". */}
        <span>{lang.toUpperCase()}</span>
      </div>
    </div>
  );
};

export default LangModeToggles;
```