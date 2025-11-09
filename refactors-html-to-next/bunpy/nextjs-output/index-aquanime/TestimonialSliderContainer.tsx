```typescript
'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Image from 'next/image';

// Define a type for a single testimonial
interface Testimonial {
  id: number;
  quote: string;
  author: string;
  role: string;
  avatar: string; // Path relative to the public directory
}

// Dummy data for testimonials. In a real application, this would likely be fetched from an API
// or passed as props.
const testimonialsData: Testimonial[] = [
  {
    id: 1,
    quote:
      "Bergabung dengan AquaNime adalah salah satu keputusan terbaik saya! Saya menemukan banyak teman baru dan bisa mengembangkan bakat saya di sini.",
    author: "- Nama Member 1",
    role: "Divisi Kreatif",
    avatar: "/assets/images/member1.png",
  },
  {
    id: 2,
    quote:
      "Dukungan yang saya dapatkan dari komunitas ini luar biasa. Ide-ide saya tidak pernah dianggap aneh, justru selalu didukung untuk berkembang.",
    author: "- Nama Member 2",
    role: "Regional Bandung",
    avatar: "/assets/images/member2.png",
  },
  {
    id: 3,
    quote:
      "Sering ada event dan kolaborasi seru. AquaNime bukan hanya komunitas, tapi keluarga yang selalu ada untuk saling belajar.",
    author: "- Nama Member 3",
    role: "Proyek Band",
    avatar: "/assets/images/member3.png",
  },
  {
    id: 4,
    quote:
      "Dari cuma suka-suka anime, sekarang saya jadi bisa nulis light novel berkat bimbingan dari para senior di sini.",
    author: "- Nama Member 4",
    role: "Divisi Konten",
    avatar: "/assets/images/member4.png",
  },
];

const TestimonialSliderContainer: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const sliderRef = useRef<HTMLDivElement>(null);
  const totalSlides = testimonialsData.length;

  // Function to navigate to a specific slide index
  const goToSlide = useCallback((index: number) => {
    setCurrentSlide(index);
  }, []);

  // Function to navigate to the next slide
  const nextSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev + 1) % totalSlides);
  }, [totalSlides]);

  // Function to navigate to the previous slide
  const prevSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides);
  }, [totalSlides]);

  // Effect to apply the transform style when the current slide changes
  // and handle responsiveness on window resize.
  useEffect(() => {
    const updateSliderPosition = () => {
      if (sliderRef.current && totalSlides > 0) {
        // Assuming each testimonial item takes up 100% of the slider's visible width.
        // The parent .testimonial-slider-container should have `overflow: hidden`.
        // The .testimonial-slider should be `display: flex; transition: transform 0.5s ease-in-out;`
        // And .testimonial-item should have `flex-shrink: 0; width: 100%;` (or a defined fixed width).
        const slideWidth = sliderRef.current.children[0]?.clientWidth || 0;
        sliderRef.current.style.transform = `translateX(-${currentSlide * slideWidth}px)`;
        // Ensure a transition property for smooth sliding, if not handled by external CSS.
        if (!sliderRef.current.style.transition) {
          sliderRef.current.style.transition = 'transform 0.5s ease-in-out';
        }
      }
    };

    // Initial positioning and whenever currentSlide changes
    updateSliderPosition();

    // Event listener for window resize to adjust slider position if layout changes
    const handleResize = () => {
      if (sliderRef.current) {
        // Temporarily disable transition to prevent visual glitches during resize
        sliderRef.current.style.transition = 'none';
        updateSliderPosition();
        // Re-enable transition after a short delay to allow layout to settle
        requestAnimationFrame(() => {
          if (sliderRef.current) {
            sliderRef.current.style.transition = 'transform 0.5s ease-in-out';
          }
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [currentSlide, totalSlides]); // Dependencies for the effect

  // Define fixed width and height for Image component. Adjust as per design.
  // For more responsive image handling, consider `fill` prop with `sizes`.
  const avatarWidth = 100;
  const avatarHeight = 100;

  return (
    <div className="testimonial-slider-container">
      <div className="testimonial-slider" ref={sliderRef}>
        {testimonialsData.map((testimonial) => (
          <div className="testimonial-item" key={testimonial.id}>
            <Image
              src={testimonial.avatar}
              alt={`Avatar of ${testimonial.author}`}
              className="testimonial-avatar"
              width={avatarWidth}
              height={avatarHeight}
              loading="lazy" // `next/image` handles lazy loading by default, but explicitly setting is fine.
            />
            <p className="futura">{testimonial.quote}</p>
            <h4>{testimonial.author}</h4>
            <span>{testimonial.role}</span>
          </div>
        ))}
      </div>
      <button className="slider-button prev-button" onClick={prevSlide} aria-label="Previous testimonial">
        <i className="fas fa-chevron-left"></i>
      </button>
      <button className="slider-button next-button" onClick={nextSlide} aria-label="Next testimonial">
        <i className="fas fa-chevron-right"></i>
      </button>
      <div className="slider-dots">
        {testimonialsData.map((_, index) => (
          <span
            key={index}
            className={`dot ${index === currentSlide ? 'active' : ''}`}
            onClick={() => goToSlide(index)}
            aria-label={`Go to slide ${index + 1}`}
          ></span>
        ))}
      </div>
    </div>
  );
};

export default TestimonialSliderContainer;
```