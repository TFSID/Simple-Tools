```typescript
// src/components/ProjectCardTitle.tsx
'use client';

import React from 'react';

interface ProjectCardTitleProps {
  /** The text content of the title. */
  children: React.ReactNode;
  /** Optional key for internationalization, mapped to `data-lang-key`. */
  langKey?: string;
  /** Additional CSS classes to apply to the title, alongside the default 'poppins' class. */
  className?: string;
}

/**
 * A client component for displaying a project card title.
 * It uses the 'poppins' font class by default and supports a `data-lang-key` attribute.
 */
const ProjectCardTitle: React.FC<ProjectCardTitleProps> = ({
  children,
  langKey,
  className,
}) => {
  return (
    <h3
      data-lang-key={langKey}
      className={`poppins ${className || ''}`.trim()}
    >
      {children}
    </h3>
  );
};

export default ProjectCardTitle;
```