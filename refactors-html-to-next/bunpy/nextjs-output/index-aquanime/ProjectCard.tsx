```tsx
'use client';

import React from 'react';

interface ProjectCardProps {
  iconClass: string; // e.g., "fas fa-hat-wizard"
  title: string;
  description: string;
  linkHref: string;
  linkText?: string; // e.g., "Selengkapnya"
  cardClasses?: string; // Optional additional classes for the card itself, e.g., "maskot-card"
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  iconClass,
  title,
  description,
  linkHref,
  linkText = 'Selengkapnya',
  cardClasses = '',
}) => {
  return (
    <div className={`project-card ${cardClasses}`}>
      <div className="icon">
        <i className={iconClass}></i>
      </div>
      <h3 className="poppins">{title}</h3>
      <p className="futura">{description}</p>
      <a href={linkHref} className="btn-primary">
        {linkText}
      </a>
    </div>
  );
};

export default ProjectCard;
```