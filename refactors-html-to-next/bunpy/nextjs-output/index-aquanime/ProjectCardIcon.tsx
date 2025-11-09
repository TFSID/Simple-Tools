```typescript
'use client';

import React from 'react';

interface ProjectCardIconProps {
  /**
   * The Font Awesome classes for the icon.
   * e.g., "fas fa-hat-wizard", "fas fa-guitar", etc.
   * Ensure Font Awesome CSS is loaded globally (e.g., in layout.tsx or global.css).
   */
  iconClass: string;
}

/**
 * A client component to display a project card icon.
 * Assumes Font Awesome CSS is loaded globally for the `fas` and icon-specific classes to work.
 * The `icon` class is expected to be defined in the project's CSS.
 */
const ProjectCardIcon: React.FC<ProjectCardIconProps> = ({ iconClass }) => {
  return (
    <div className="icon">
      <i className={iconClass}></i>
    </div>
  );
};

export default ProjectCardIcon;
```