```tsx
'use client';

import React from 'react';

interface SectionHeadingProps {
  /** The main heading text, can include React nodes for rich content (e.g., <br />). */
  title: string | React.ReactNode;
  /** Optional subtitle text, displayed as a paragraph below the heading. */
  subtitle?: string | React.ReactNode;
  /** Additional CSS classes for the main container div (e.g., "container text-center animate-target"). */
  className?: string;
  /** Additional CSS classes for the h2 element (e.g., "poppins", "projects-page-title"). */
  titleClassName?: string;
  /** Additional CSS classes for the p element (e.g., "futura"). */
  subtitleClassName?: string;
  /** Inline CSS properties for the h2 element. */
  titleStyle?: React.CSSProperties;
  /** Optional data-lang-key attribute for the h2 element, used for localization. */
  dataLangKey?: string;
}

/**
 * A reusable client component for displaying a section heading with an optional subtitle.
 * It encapsulates the common structure of a heading block as found in the provided HTML.
 *
 * It typically renders:
 * `<div className="container text-center animate-target ... (className)">`
 *   `<h2 className="poppins ... (titleClassName)" style={titleStyle} data-lang-key={dataLangKey}>`
 *     `{title}`
 *   `</h2>`
 *   `<p className="futura ... (subtitleClassName)">`
 *     `{subtitle}`
 *   `</p>`
 * `</div>`
 */
const SectionHeading: React.FC<SectionHeadingProps> = ({
  title,
  subtitle,
  className,
  titleClassName,
  subtitleClassName,
  titleStyle,
  dataLangKey,
}) => {
  // Common classes observed in the HTML for section headings and their containers.
  // These are defaults and can be overridden or extended by passed props.
  const defaultContainerClasses = 'container text-center animate-target';
  const defaultTitleClasses = 'poppins'; // Many h2 elements have 'poppins'
  const defaultSubtitleClasses = 'futura'; // Many p elements have 'futura'

  return (
    <div className={`${defaultContainerClasses} ${className || ''}`}>
      <h2
        className={`${defaultTitleClasses} ${titleClassName || ''}`}
        style={titleStyle}
        // Conditionally apply data-lang-key if provided
        {...(dataLangKey && { 'data-lang-key': dataLangKey })}
      >
        {title}
      </h2>
      {subtitle && (
        <p className={`${defaultSubtitleClasses} ${subtitleClassName || ''}`}>
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default SectionHeading;
```