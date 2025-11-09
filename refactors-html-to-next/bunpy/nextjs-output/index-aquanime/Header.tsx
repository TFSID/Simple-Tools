'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';

interface HeaderProps {}

const Header: React.FC<HeaderProps> = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Initial check for dark mode from localStorage on component mount
    try {
      const storedDarkMode = localStorage.getItem('aquanimeDarkMode');
      if (storedDarkMode === 'true') {
        setIsDarkMode(true);
        // Apply dark-mode class to body immediately if stored
        document.body.classList.add('dark-mode');
      }
    } catch (e) {
      console.error("Failed to read dark mode from localStorage", e);
    }
  }, []); // Empty dependency array means this runs once on mount

  useEffect(() => {
    // Sync the 'dark-mode' class on the body and localStorage with the component's state
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    try {
      localStorage.setItem('aquanimeDarkMode', isDarkMode.toString());
    } catch (e) {
      console.error("Failed to save dark mode to localStorage", e);
    }
  }, [isDarkMode]); // Runs whenever isDarkMode state changes

  const handleDarkModeToggle = () => {
    setIsDarkMode(prevMode => !prevMode);
  };

  return (
    <header>
      <nav>
        <div className="logo">
          {/* Using next/image for optimized image loading.
              Assuming 'assets/images/logo.png' is located in the 'public' directory. */}
          <Image 
            src="/assets/images/logo.png" 
            alt="AquaNime Logo" 
            width={50} // Specify width and height for Image component optimization
            height={50} 
            priority // Prioritize loading for LCP
          />
          <span>AquaNime</span>
        </div>
        <ul id="nav-links" className="poppins">
          {/* Using next/link for client-side navigation */}
          <li><Link href="/">BERANDA</Link></li>
          <li><Link href="/pages/tentang">TENTANG</Link></li>
          <li><Link href="/pages/proyek">PROYEK</Link></li>
          <li><Link href="/pages/portal">PORTAL</Link></li>
          <li><Link href="/pages/kontak">KONTAK</Link></li>
        </ul>
        <div className="lang-mode-toggles poppins">
          <div className="dark-mode-toggle" id="dark-mode-toggle" onClick={handleDarkModeToggle}>
            {/* Toggle icon and text based on dark mode state */}
            <i className={`fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}`}></i>{' '}
            <span>{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
          </div>
        </div>
        <div className="social-icons">
          <a href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></a>
          <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
          <a href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></a>
          <a href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></a>
          <a href="#" aria-label="Discord"><i className="fab fa-discord"></i></a>
        </div>
        <div className="hamburger-menu" id="sidebar">
          <i className="fas fa-bars"></i>
        </div>
      </nav>
    </header>
  );
};

export default Header;