import React from 'react';
import styles from './Footer.module.css';

interface FooterProps {
  /**
   * Optional CSS class to apply custom styles to the footer.
   */
  className?: string;
}

const Footer: React.FC<FooterProps> = ({ className }) => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={`${styles.footer} ${className || ''}`.trim()}>
      <div className={styles.container}>
        <p className={styles.copyright}>
          &copy; {currentYear} My Awesome App. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;