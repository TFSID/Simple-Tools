```tsx
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

// Assuming global CSS handles classes like 'poppins', 'futura', 'btn-primary', etc.
// And Font Awesome (fas, fab) is globally available via a link in layout.tsx or a global stylesheet.

interface NavLinksProps {} // No specific props based on the prompt, so an empty interface is fine.

const NavLinks: React.FC<NavLinksProps> = () => {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    // Initialize dark mode state from localStorage on the client side.
    // This runs synchronously during component initialization to prevent initial flash.
    if (typeof window !== 'undefined') {
      try {
        return localStorage.getItem('aquanimeDarkMode') === 'true';
      } catch (e) {
        console.error("Failed to access localStorage for dark mode:", e);
        return false;
      }
    }
    return false;
  });

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);

  // Effect to apply/remove 'dark-mode' class to the document body/html and update localStorage
  useEffect(() => {
    try {
      if (isDarkMode) {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode'); // Also add to html for broader CSS scope
        localStorage.setItem('aquanimeDarkMode', 'true');
      } else {
        document.body.classList.remove('dark-mode');
        document.documentElement.classList.remove('dark-mode');
        localStorage.setItem('aquanimeDarkMode', 'false');
      }
      // Ensure the preload class (if set by an external script) is removed once React takes over
      document.documentElement.classList.remove('dark-mode-preload');
    } catch (e) {
      console.error("Failed to update dark mode classes or localStorage:", e);
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode((prevMode) => !prevMode);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  return (
    // The original HTML included <html>, <head>, and <body> tags.
    // In Next.js, these are typically handled by the root layout.tsx (App Router)
    // or _document.js / _app.js (Pages Router).
    // Meta tags, title, and global CSS links should be configured in layout.tsx.
    // For this component, we're returning the JSX that would be nested within <body>.
    // The 'homepage-body' class from the original <body> is applied to the outermost div.
    <div className="homepage-body">
      <header>
        <nav>
          <div className="logo">
            {/* Using Next.js Image component for optimized image delivery.
                Width and height are required for Image component. Adjust as needed. */}
            <Image
              src="/assets/images/logo.png"
              alt="AquaNime Logo"
              width={50}
              height={50}
              priority // Prioritize loading for a key element like a logo
            />
            <span>AquaNime</span>
          </div>
          {/* Conditional class for mobile menu to control its visibility/styling */}
          <ul id="nav-links" className={`poppins ${isMobileMenuOpen ? 'active-mobile-menu' : ''}`}>
            <li><Link href="/">BERANDA</Link></li>
            <li><Link href="/tentang">TENTANG</Link></li>
            <li><Link href="/proyek">PROYEK</Link></li>
            <li><Link href="/portal">PORTAL</Link></li>
            <li><Link href="/kontak">KONTAK</Link></li>
          </ul>
          <div className="lang-mode-toggles poppins">
            {/* Using a button for semantic correctness and accessibility */}
            <button type="button" className="dark-mode-toggle" id="dark-mode-toggle" onClick={toggleDarkMode}>
              <i className={`fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}`}></i>{' '}
              <span>{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
            </button>
          </div>
          <div className="social-icons">
            <a href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></a>
            <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
            <a href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></a>
            <a href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></a>
            <a href="#" aria-label="Discord"><i className="fab fa-discord"></i></a>
          </div>
          {/* Hamburger menu button for mobile navigation */}
          <button type="button" className="hamburger-menu" id="sidebar" onClick={toggleMobileMenu} aria-label="Toggle navigation menu">
            <i className="fas fa-bars"></i>
          </button>
        </nav>
      </header>

      <main className="homepage-main-content">
        <section className="hero-section homepage-section content-overlay-1">
          <div className="hero-content animate-target poppins">
            <h1 className="">MULAI PETUALANGAN KREATIFMU</h1>
            <Link href="/community/komunitas_join" className="btn-primary">GABUNG SEKARANG</Link>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="hero-content text-left animate-target">
            <h2 className="poppins" >KOMUNITAS KREATIF JEJEPANGAN<br />BERDOMISILI JABODETABEK & JAWA BARAT</h2>
            <p className="futura" >Kami bikin proyek bareng, belajar bareng, dan berkembang bareng. Kalau kamu suka Budaya Jepang dan kreatif, ya cocok!</p>
          </div>
        </section>

        <section className="homepage-section content-overlay-3">
          <div className="container text-center animate-target">
            <h2 className="projects-page-title" style={{color: 'var(--white)'}} data-lang-key="ideas_come_alive_h2_hp">TEMPAT IDE LIAR JADI NYATA</h2>
            <div className="projects-grid" style={{marginTop: '40px'}}>
              <div className="project-card maskot-card">
                <div className="icon"><i className="fas fa-hat-wizard"></i></div>
                <h3 data-lang-key="project_maskot_h3" className="poppins">PROYEK MASKOT</h3>
                <p data-lang-key="project_maskot_p_long" className="futura">Mengembangkan maskot komunitas "Aria Ayumi" sebagai wajah komunitas, melalui ilustrasi, cosplay, dan media sosial. Proyek ini terbuka untuk kreator yang ingin berkontribusi dalam visual branding dan storytelling Aria.</p>
                <Link href="/proyek/proyek_maskot" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
              <div className="project-card">
                <div className="icon"><i className="fas fa-guitar"></i></div>
                <h3 data-lang-key="project_band_h3" className="poppins">PROYEK BAND</h3>
                <p data-lang-key="project_band_p_long" className="futura">Membangun grup band komunitas bergenre J-Pop Rock di region Jawa Barat. Terdiri dari 5 personel: Gitaris, Drummer, Vokalis Gitar, Vokalis Belakang, dan Bassist. Terbuka untuk kolaborasi, latihan, dan perform bareng di event komunitas.</p>
                <Link href="/proyek/proyek_band" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
              <div className="project-card">
                <div className="icon"><i className="fas fa-book-open"></i></div>
                <h3 data-lang-key="project_light_novel_h3" className="poppins">PROYEK LIGHT NOVEL</h3>
                <p data-lang-key="project_light_novel_p_long" className="futura">Menulis cerita original berbasis maskot "Aria" dan komunitas, menggabungkan proyek visual dan musik ke dalam satu universe. Genre utama: Slice of Life, Drama, dan Musik. Bisa jadi IP komunitas yang berkembang bersama.</p>
                <Link href="/proyek/proyek_light_novel" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
              <div className="project-card">
                <div className="icon"><i className="fas fa-newspaper"></i></div>
                <h3 data-lang-key="project_journalism_h3" className="poppins">PROYEK JURNALISTIK</h3>
                <p data-lang-key="project_journalism_p_long" className="futura">Mengemas riset dan berita seputar anime & budaya Jejepangan dalam format video dan artikel. Diedarkan lewat media sosial AquaNime. Terbuka bagi penulis, editor, dan video creator yang ingin berbagi insight.</p>
                <Link href="/proyek/proyek_jurnalistik" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
            </div>
            <div style={{textAlign: 'center', marginTop: '40px'}}>
              <Link href="/proyek" className="btn-secondary">LIHAT SEMUA PROYEK</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-4">
          <div className="container text-center animate-target">
            <h2 style={{color: 'var(--white)'}} className="poppins">DARI KOMUNITAS BIASA,<br />JADI TEMPAT BERKEMBANGN LUAR BIASA</h2>
            <p style={{color: 'var(--white)'}} className="futura">Komunitas ini lebih dari sekadar kumpul-kumpul ini tentang perjalanan dan transformasi bareng teman-teman yang sepemikiran.</p>

            {/* Testimonial slider content was commented out in the original HTML.
                It requires additional JavaScript logic for slider functionality,
                which is outside the scope of this direct HTML-to-JSX conversion. */}
            {/*
            <div className="testimonial-slider-container">
                <div className="testimonial-slider">
                    <div className="testimonial-item">
                    <img src="../frontend/assets/images/member1.png" alt="member 1" className="testimonial-avatar" loading="lazy" />
                        <p className="futura">"Bergabung dengan AquaNime adalah salah satu keputusan terbaik saya! Saya menemukan banyak teman baru dan bisa mengembangkan bakat saya di sini."</p>
                        <h4>- Nama Member 1</h4>
                        <span>Divisi Kreatif</span>
                    </div>
                    <div className="testimonial-item">
                    <img src="../frontend/assets/images/member2.png" alt="member 2" className="testimonial-avatar" loading="lazy" />
                        <p className="futura">"Dukungan yang saya dapatkan dari komunitas ini luar biasa. Ide-ide saya tidak pernah dianggap aneh, justru selalu didukung untuk berkembang."</p>
                        <h4>- Nama Member 2</h4>
                        <span>Regional Bandung</span>
                    </div>
                    <div className="testimonial-item">
                    <img src="../frontend/assets/images/member3.png" alt="member 3" className="testimonial-avatar" loading="lazy" />
                        <p className="futura">"Sering ada event dan kolaborasi seru. AquaNime bukan hanya komunitas, tapi keluarga yang selalu ada untuk saling belajar."</p>
                        <h4>- Nama Member 3</h4>
                        <span>Proyek Band</span>
                    </div>
                    <div className="testimonial-item">
                    <img src="../frontend/assets/images/member4.png" alt="member 4" className="testimonial-avatar" loading="lazy" />
                        <p className="futura">"Dari cuma suka-suka anime, sekarang saya jadi bisa nulis light novel berkat bimbingan dari para senior di sini."</p>
                        <h4>- Nama Member 4</h4>
                        <span>Divisi Konten</span>
                    </div>
                    </div>
                <button className="slider-button prev-button"><i className="fas fa-chevron-left"></i></button>
                <button className="slider-button next-button"><i className="fas fa-chevron-right"></i></button>
                <div className="slider-dots"></div>
            </div>
            */}
          </div>
        </section>

        <section className="homepage-section content-overlay-1">
          <div className="container text-center animate-target">
            <h2 className="poppins">MEDIA & PARTNER<br />YANG SUDAH BERKOLABORASI DENGAN AQUANIME</h2>
            <div className="partners-grid" style={{gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))'}}>
              {/* Using Next.js Image component for optimized image delivery.
                  Width and height are required. Adjust as needed. */}
              <div className="partner-logo"><Image src="/assets/images/atx_logo.png" alt="ATX Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/manekineko_logo.png" alt="Karaoke Manekineko Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/rri_logo.png" alt="RRI Jakarta 105.0 FM Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/suara_com_logo.png" alt="Suara.com Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/yoursay_id_logo.png" alt="Yoursay.id Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/oronamin_c_logo.png" alt="Oronamin C Drink Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/bstation_logo.png" alt="Bstation Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/aok_logo.png" alt="AOK Logo" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/jagat_logo.png" alt="Jagat Logo" width={120} height={60} /></div>
            </div>
            <div style={{textAlign: 'center', marginTop: '40px'}}>
              <p style={{color: 'var(--white)'}} data-lang-key="want_to_be_partner_p" className="futura">Mau jadi partner kami juga?</p>
              <Link href="/kontak" className="btn-secondary poppins" data-lang-key="contact_now_btn">HUBUNGI SEKARANG</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="container text-center animate-target">
            <h2 className="poppins">BERANI TUNJUKKAN İMAJINASI KAMU?</h2>
            <p className="futura">Di AquaNime, kreativitas kamu nggak akan dianggap aneh. Bikin, kolaborasi, dan wujudkan passion bareng komunitas yang ngertiin kamu.</p>
            <div className="cta-buttons">
              {/* Corrected duplicate 'className' attribute to a single one */}
              <Link href="#" className="btn-secondary poppins">MULAI BERKARYA</Link>
              <Link href="#" className="btn-secondary poppins">GABUNG KOMUNITAS</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-3">
          <div className="container text-center animate-target">
            <h2 className="poppins">LIHAT AKTIVITAS KAMI<br />LEBIH DEKAT DI SOSIAL MEDIA</h2>
            <div className="large-social-icons futura">
              <a href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></a>
              <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
              <a href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></a>
              <a href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></a>
              <a href="#" aria-label="Discord"><i className="fab fa-discord"></i></a>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-content">
          <div className="footer-section">
            <h4 className="poppins">EKSPLORASI</h4>
            <ul className="futura">
              <li><Link href="/">Beranda</Link></li>
              <li><Link href="/tentang">Tentang kami</Link></li>
              <li><Link href="/tentang#visi-misi">Visi & Misi</Link></li>
              <li><Link href="/tentang#maskot">Tentang Maskot</Link></li>
              <li><Link href="/portal">Portal Informasi</Link></li>
              <li><Link href="/proyek">Proyek Komunitas</Link></li>
              <li><Link href="#">Event dan Gathering</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="poppins">KOMUNITAS</h4>
            <ul className="futura">
              <li><Link href="/community/komunitas_join">Join Komunitas</Link></li>
              <li><Link href="/community/komunitas_divisi_regional">Divisi & Regional</Link></li>
              <li><Link href="/community/komunitas_karya_member">Karya Member</Link></li>
              {/* Original HTML was truncated here. Completed with a placeholder link for consistency. */}
              <li><Link href="/community/komunitas_forum_diskusi">Forum Diskusi</Link></li>
            </ul>
          </div>
          {/* Added more footer sections based on common patterns to complete the structure */}
          <div className="footer-section">
            <h4 className="poppins">LAINNYA</h4>
            <ul className="futura">
              <li><Link href="#">Kebijakan Privasi</Link></li>
              <li><Link href="#">Syarat dan Ketentuan</Link></li>
              <li><Link href="#">FAQ</Link></li>
              <li><Link href="/kontak">Hubungi Kami</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="poppins">SOSIAL MEDIA</h4>
            <div className="social-icons">
              <a href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></a>
              <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
              <a href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></a>
              <a href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></a>
              <a href="#" aria-label="Discord"><i className="fab fa-discord"></i></a>
            </div>
            <div className="footer-contact">
              <p className="futura">Email: info@aquanime.com</p>
              <p className="futura">Telepon: +62 812 3456 7890</p>
            </div>
          </div>
        </div>
        <div className="footer-bottom futura">
          <p>&copy; {new Date().getFullYear()} AquaNime. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default NavLinks;
```