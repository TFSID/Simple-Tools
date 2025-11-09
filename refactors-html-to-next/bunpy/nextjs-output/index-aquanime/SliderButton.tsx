```typescript
'use client';

import React from 'react';

/**
 * Props for the SliderButton component.
 */
interface SliderButtonProps {
  /**
   * The direction of the slider button. Determines the icon and base styling.
   * 'prev' for a left-facing chevron, 'next' for a right-facing chevron.
   */
  direction: 'prev' | 'next';
  /**
   * Function to be called when the button is clicked.
   */
  onClick: () => void;
  /**
   * Optional ARIA label for accessibility. If not provided, a default will be used.
   */
  ariaLabel?: string;
  /**
   * Optional additional CSS classes to apply to the button.
   */
  className?: string;
}

/**
 * A reusable client component for navigation buttons within a slider or carousel.
 * It automatically applies Font Awesome chevron icons based on the 'direction' prop.
 *
 * This component assumes Font Awesome CSS is globally available (e.g., linked in `layout.tsx` or `globals.css`).
 */
const SliderButton: React.FC<SliderButtonProps> = ({
  direction,
  onClick,
  ariaLabel,
  className,
}) => {
  const iconClass = direction === 'prev' ? 'fas fa-chevron-left' : 'fas fa-chevron-right';
  const defaultAriaLabel = direction === 'prev' ? 'Previous slide' : 'Next slide';
  const baseClasses = `slider-button ${direction}-button`;

  return (
    <button
      className={`${baseClasses} ${className || ''}`.trim()}
      onClick={onClick}
      aria-label={ariaLabel || defaultAriaLabel}
    >
      <i className={iconClass} aria-hidden="true"></i>
    </button>
  );
};

export default SliderButton;
```