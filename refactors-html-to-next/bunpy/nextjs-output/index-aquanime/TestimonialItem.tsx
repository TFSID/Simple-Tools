```tsx
'use client';

import React from 'react';

interface TestimonialItemProps {
  imageSrc: string;
  imageAlt: string;
  quote: string;
  name: string;
  title: string;
}

const TestimonialItem: React.FC<TestimonialItemProps> = ({
  imageSrc,
  imageAlt,
  quote,
  name,
  title,
}) => {
  return (
    <div className="testimonial-item">
      <img src={imageSrc} alt={imageAlt} className="testimonial-avatar" loading="lazy" />
      <p className="futura">"{quote}"</p>
      <h4>- {name}</h4>
      <span>{title}</span>
    </div>
  );
};

export default TestimonialItem;
```