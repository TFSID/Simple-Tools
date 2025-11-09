```tsx
'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

// --- Font Best Practices ---
// For better performance and FOUC prevention, it's recommended to use `next/font`.
// You would typically define your fonts in `app/layout.tsx` (App Router)
// or globally and then apply them via className.
//
// Example for Poppins (assuming it's a Google Font):
// import { Poppins } from 'next/font/google';
// const poppins = Poppins({
//   subsets: ['latin'],
//   weight: ['400', '600', '700'], // Adjust weights as used in CSS
//   variable: '--font-poppins', // Define a CSS variable if needed
// });
//
// Then in your root layout:
// <html lang="id" className={`${poppins.variable} ${futura.variable}`}>...</html>
// And in CSS:
// .poppins { font-family: var(--font-poppins), sans-serif; }
//
// For custom fonts like Futura Std 4 from CDNFonts, you might need to self-host
// or load them via CSS in a global stylesheet imported in `layout.tsx`.
// For this conversion, the original class names (`poppins`, `futura`) are kept,
// assuming the global CSS handling for these fonts is in place.

interface HeroContentBlockProps {
  // Define any props here if your component needs to receive data
  // For this direct HTML conversion, no specific props are immediately apparent.
}

const HeroContentBlock: React.FC<HeroContentBlockProps> = () => {
  // --- Client-Side Script Conversion ---
  // The original HTML included an inline script for dark mode preload and
  // presumed JavaScript for toggling dark mode and a sidebar.
  // In a Next.js client component, such logic is best handled using `useEffect`.

  useEffect(() => {
    // 1. Dark Mode Preload Script (to prevent white flash on reload)
    // For optimal "no flash" behavior, this specific preload logic is often
    // placed as an inline <script> directly in `app/layout.tsx` (App Router)
    // or `pages/_document.tsx` (Pages Router) before React hydrates.
    // Placing it in `useEffect` here means it runs *after* the component mounts,
    // which might still result in a brief flash in some scenarios.
    try {
      if (localStorage.getItem('aquanimeDarkMode') === 'true') {
        document.documentElement.classList.add('dark-mode-preload');
        document.body.classList.add('dark-mode');
      }
    } catch (e) {
      console.error('Error applying dark mode preload:', e);
    }

    // 2. Event Listeners for Dark Mode Toggle and Sidebar
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const sidebarToggle = document.getElementById('sidebar'); // Hamburger menu
    const navLinks = document.getElementById('nav-links'); // Navigation links to toggle

    const handleDarkModeToggle = () => {
      document.body.classList.toggle('dark-mode');
      const isDarkMode = document.body.classList.contains('dark-mode');
      localStorage.setItem('aquanimeDarkMode', isDarkMode.toString());
      // Optionally remove 'dark-mode-preload' after first interaction
      document.documentElement.classList.remove('dark-mode-preload');
    };

    const handleSidebarToggle = () => {
      if (navLinks) {
        navLinks.classList.toggle('active'); // Assumes you have CSS for `.active` state
        // You might also toggle a class on the body or header to control overlay/blur
      }
    };

    if (darkModeToggle) {
      darkModeToggle.addEventListener('click', handleDarkModeToggle);
    }
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', handleSidebarToggle);
    }

    // Cleanup event listeners when the component unmounts
    return () => {
      if (darkModeToggle) {
        darkModeToggle.removeEventListener('click', handleDarkModeToggle);
      }
      if (sidebarToggle) {
        sidebarToggle.removeEventListener('click', handleSidebarToggle);
      }
    };
  }, []); // Empty dependency array ensures this runs once on mount and cleans up on unmount

  return (
    // The component returns the content that would typically be inside the `<body>` tag.
    // The `homepage-body` class is applied to the outermost element here.
    <div className="homepage-body">
      {/* Header Section */}
      <header>
        <nav>
          <div className="logo">
            {/* Using Next.js Image component for optimization */}
            {/* Width and height are guesses; replace with actual image dimensions */}
            <Image src="/assets/images/logo.png" alt="AquaNime Logo" width={40} height={40} priority />
            <span>AquaNime</span>
          </div>
          <ul id="nav-links" className="poppins">
            <li><Link href="/">BERANDA</Link></li>
            <li><Link href="/tentang">TENTANG</Link></li>
            <li><Link href="/proyek">PROYEK</Link></li>
            <li><Link href="/portal">PORTAL</Link></li>
            <li><Link href="/kontak">KONTAK</Link></li>
          </ul>
          <div className="lang-mode-toggles poppins">
            <div className="dark-mode-toggle" id="dark-mode-toggle">
              <i className="fas fa-moon"></i> <span>Dark Mode</span>
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

      {/* Main Content Area */}
      <main className="homepage-main-content">
        <section className="hero-section homepage-section content-overlay-1">
          <div className="hero-content animate-target poppins">
            <h1 className="">MULAI PETUALANGAN KREATIFMU</h1>
            <Link href="/community/komunitas_join" className="btn-primary">GABUNG SEKARANG</Link>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="hero-content text-left animate-target">
            <h2 className="poppins">KOMUNITAS KREATIF JEJEPANGAN<br />BERDOMISILI JABODETABEK & JAWA BARAT</h2>
            <p className="futura">Kami bikin proyek bareng, belajar bareng, dan berkembang bareng. Kalau kamu suka Budaya Jepang dan kreatif, ya cocok!</p>
          </div>
        </section>

        <section className="homepage-section content-overlay-3">
          <div className="container text-center animate-target">
            {/* Inline style converted to JSX style object */}
            <h2 className="projects-page-title" style={{ color: 'var(--white)' }} data-lang-key="ideas_come_alive_h2_hp">TEMPAT IDE LIAR JADI NYATA</h2>
            <div className="projects-grid" style={{ marginTop: '40px' }}>
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
            <div style={{ textAlign: 'center', marginTop: '40px' }}>
              <Link href="/proyek" className="btn-secondary">LIHAT SEMUA PROYEK</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-4">
          <div className="container text-center animate-target">
            <h2 style={{ color: 'var(--white)' }} className="poppins">DARI KOMUNITAS BIASA,<br />JADI TEMPAT BERKEMBANGN LUAR BIASA</h2>
            <p style={{ color: 'var(--white)' }} className="futura">Komunitas ini lebih dari sekadar kumpul-kumpul ini tentang perjalanan dan transformasi bareng teman-teman yang sepemikiran.</p>

            {/* Testimonial slider section (commented out in original HTML) */}
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
            {/* Inline style for grid converted to JSX style object */}
            <div className="partners-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
              {/* Using Next.js Image component for optimization, guessing common logo aspect ratios */}
              <div className="partner-logo"><Image src="/assets/images/atx_logo.png" alt="ATX Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/manekineko_logo.png" alt="Karaoke Manekineko Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/rri_logo.png" alt="RRI Jakarta 105.0 FM Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/suara_com_logo.png" alt="Suara.com Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/yoursay_id_logo.png" alt="Yoursay.id Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/oronamin_c_logo.png" alt="Oronamin C Drink Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/bstation_logo.png" alt="Bstation Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/aok_logo.png" alt="AOK Logo" width={120} height={48} /></div>
              <div className="partner-logo"><Image src="/assets/images/jagat_logo.png" alt="Jagat Logo" width={120} height={48} /></div>
            </div>
            <div style={{ textAlign: 'center', marginTop: '40px' }}>
              <p style={{ color: 'var(--white)' }} data-lang-key="want_to_be_partner_p" className="futura">Mau jadi partner kami juga?</p>
              <Link href="/kontak" className="btn-secondary poppins" data-lang-key="contact_now_btn">HUBUNGI SEKARANG</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="container text-center animate-target">
            <h2 className="poppins">BERANI TUNJUKKAN İMAJINASI KAMU?</h2>
            <p className="futura">Di AquaNime, kreativitas kamu nggak akan dianggap aneh. Bikin, kolaborasi, dan wujudkan passion bareng komunitas yang ngertiin kamu.</p>
            <div className="cta-buttons">
              {/* Corrected duplicate `className` attributes */}
              <a href="#" className="btn-secondary poppins">MULAI BERKARYA</a>
              <a href="#" className="btn-secondary poppins">GABUNG KOMUNITAS</a>
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

      {/* Footer Section */}
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
              <li><Link href="#">Event dan Gathering</Link></li> {/* Non-Next.js internal link */}
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="poppins">KOMUNITAS</h4>
            <ul className="futura">
              <li><Link href="/community/komunitas_join">Join Komunitas</Link></li>
              <li><Link href="/community/komunitas_divisi_regional">Divisi & Regional</Link></li>
              <li><Link href="/community/komunitas_karya_member">Karya Member</Link></li>
              {/* The original HTML was truncated here, completing the link and closing the list */}
              <li><Link href="/community/komunitas_forum_diskusi">Forum Diskusi</Link></li>
              {/* Add more footer links if they were part of the original source beyond the truncation */}
            </ul>
          </div>
          {/* If there were more footer sections in the original HTML, they would go here. */}
        </div>
      </footer>
    </div>
  );
};

export default HeroContentBlock;
```