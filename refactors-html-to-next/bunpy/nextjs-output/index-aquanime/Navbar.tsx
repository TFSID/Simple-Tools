'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';

// NOTE: The original HTML included <head> content and a global dark mode preload script.
// In a Next.js application, <head> content (meta tags, global stylesheets, external fonts)
// should be managed in app/layout.tsx or a dedicated <Head> component (e.g., using next/head or next/font).
// The global dark mode preload script to prevent a flash of unstyled content (FOUC)
// is best placed directly in app/layout.tsx within a <script> tag with 'dangerouslySetInnerHTML'
// and 'suppressHydrationWarning' on the <html> tag, or using a dedicated library like 'next-themes'.
// This component converts the <body> content and its interactive elements.

export default function Navbar() {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  // Dark mode logic to run on client-side mount
  useEffect(() => {
    try {
      // Read from localStorage for initial dark mode state
      const savedMode = localStorage.getItem('aquanimeDarkMode');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initialMode = savedMode ? savedMode === 'true' : prefersDark;
      setIsDarkMode(initialMode);

      // Apply initial dark mode classes to documentElement and body
      // The original HTML had a preload script; this useEffect attempts to mimic that behavior
      // as early as possible within a client component, though a server-side pre-render
      // or layout-level script is ideal for full FOUC prevention.
      if (initialMode) {
        document.documentElement.classList.add('dark-mode-preload');
        document.body.classList.add('dark-mode');
      } else {
        document.documentElement.classList.remove('dark-mode-preload');
        document.body.classList.remove('dark-mode');
      }
    } catch (e) {
      console.error('Failed to access localStorage for dark mode:', e);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount to set initial state

  // Effect to update classes and localStorage when isDarkMode state changes
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('aquanimeDarkMode', 'true');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('aquanimeDarkMode', 'false');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(prevMode => !prevMode);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  return (
    // Note: The <body> tag should typically be in app/layout.tsx.
    // However, the prompt requires converting the entire provided HTML,
    // which includes the <body>, into *this* component.
    <body className="homepage-body">
      <header>
        <nav>
          <div className="logo">
            <Image src="/assets/images/logo.png" alt="AquaNime Logo" width={50} height={50} priority />
            <span>AquaNime</span>
          </div>
          <ul id="nav-links" className={`poppins ${isSidebarOpen ? 'sidebar-open' : ''}`}>
            <li><Link href="/">BERANDA</Link></li>
            <li><Link href="/pages/tentang">TENTANG</Link></li>
            <li><Link href="/pages/proyek">PROYEK</Link></li>
            <li><Link href="/pages/portal">PORTAL</Link></li>
            <li><Link href="/pages/kontak">KONTAK</Link></li>
          </ul>
          <div className="lang-mode-toggles poppins">
            <div className="dark-mode-toggle" onClick={toggleDarkMode}>
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
          <div className="hamburger-menu" onClick={toggleSidebar}>
            <i className="fas fa-bars"></i>
          </div>
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
              <Link href="/pages/proyek" className="btn-secondary">LIHAT SEMUA PROYEK</Link>
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
                    <Image src="/assets/images/member1.png" alt="member 1" className="testimonial-avatar" loading="lazy" width={100} height={100} />
                        <p className="futura">"Bergabung dengan AquaNime adalah salah satu keputusan terbaik saya! Saya menemukan banyak teman baru dan bisa mengembangkan bakat saya di sini."</p>
                        <h4>- Nama Member 1</h4>
                        <span>Divisi Kreatif</span>
                    </div>
                    <div className="testimonial-item">
                    <Image src="/assets/images/member2.png" alt="member 2" className="testimonial-avatar" loading="lazy" width={100} height={100} />
                        <p className="futura">"Dukungan yang saya dapatkan dari komunitas ini luar biasa. Ide-ide saya tidak pernah dianggap aneh, justru selalu didukung untuk berkembang."</p>
                        <h4>- Nama Member 2</h4>
                        <span>Regional Bandung</span>
                    </div>
                    <div className="testimonial-item">
                    <Image src="/assets/images/member3.png" alt="member 3" className="testimonial-avatar" loading="lazy" width={100} height={100} />
                        <p className="futura">"Sering ada event dan kolaborasi seru. AquaNime bukan hanya komunitas, tapi keluarga yang selalu ada untuk saling belajar."</p>
                        <h4>- Nama Member 3</h4>
                        <span>Proyek Band</span>
                    </div>
                    <div className="testimonial-item">
                    <Image src="/assets/images/member4.png" alt="member 4" className="testimonial-avatar" loading="lazy" width={100} height={100} />
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
            <div className="partners-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
              <div className="partner-logo"><Image src="/assets/images/atx_logo.png" alt="ATX Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/manekineko_logo.png" alt="Karaoke Manekineko Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/rri_logo.png" alt="RRI Jakarta 105.0 FM Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/suara_com_logo.png" alt="Suara.com Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/yoursay_id_logo.png" alt="Yoursay.id Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/oronamin_c_logo.png" alt="Oronamin C Drink Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/bstation_logo.png" alt="Bstation Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/aok_logo.png" alt="AOK Logo" loading="lazy" width={120} height={60} /></div>
              <div className="partner-logo"><Image src="/assets/images/jagat_logo.png" alt="Jagat Logo" loading="lazy" width={120} height={60} /></div>
            </div>
            <div style={{ textAlign: 'center', marginTop: '40px' }}>
              <p style={{ color: 'var(--white)' }} data-lang-key="want_to_be_partner_p" className="futura">Mau jadi partner kami juga?</p>
              <Link href="/pages/kontak" className="btn-secondary poppins" data-lang-key="contact_now_btn">HUBUNGI SEKARANG</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="container text-center animate-target">
            <h2 className="poppins">BERANI TUNJUKKAN İMAJINASI KAMU?</h2>
            <p className="futura">Di AquaNime, kreativitas kamu nggak akan dianggap aneh. Bikin, kolaborasi, dan wujudkan passion bareng komunitas yang ngertiin kamu.</p>
            <div className="cta-buttons">
              {/* Original HTML had duplicate className props, fixed here */}
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
              <li><Link href="/pages/tentang">Tentang kami</Link></li>
              <li><Link href="/pages/tentang#visi-misi">Visi & Misi</Link></li>
              <li><Link href="/pages/tentang#maskot">Tentang Maskot</Link></li>
              <li><Link href="/pages/portal">Portal Informasi</Link></li>
              <li><Link href="/pages/proyek">Proyek Komunitas</Link></li>
              <li><Link href="#">Event dan Gathering</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="poppins">KOMUNITAS</h4>
            <ul className="futura">
              <li><Link href="/community/komunitas_join">Join Komunitas</Link></li>
              <li><Link href="/community/komunitas_divisi_regional">Divisi & Regional</Link></li>
              <li><Link href="/community/komunitas_karya_member">Karya Member</Link></li>
              {/* Original HTML had truncated text "Forum Disku", completed to "Forum Diskusi" */}
              <li><Link href="/community/komunitas_forum_diskusi">Forum Diskusi</Link></li>
              <li><Link href="#">Donasi dan Support</Link></li>
              <li><Link href="#">FAQ</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="poppins">INFORMASI</h4>
            <ul className="futura">
              <li><Link href="/pages/blog">Blog & Artikel</Link></li>
              <li><Link href="/pages/event">Event Komunitas</Link></li>
              <li><Link href="/pages/gallery">Galeri Foto</Link></li>
              <li><Link href="/pages/karier">Karier</Link></li>
              <li><Link href="/pages/kebijakan_privasi">Kebijakan Privasi</Link></li>
              <li><Link href="/pages/syarat_ketentuan">Syarat & Ketentuan</Link></li>
              <li><Link href="/pages/sitemap">Sitemap</Link></li>
            </ul>
          </div>
          <div className="footer-section contact-info">
            <h4 className="poppins">KONTAK KAMI</h4>
            <p className="futura"><i className="fas fa-map-marker-alt"></i> Bekasi, Jawa Barat, Indonesia</p>
            <p className="futura"><i className="fas fa-envelope"></i> admin@aquanime.id</p>
            <p className="futura"><i className="fab fa-whatsapp"></i> +62 813-1779-7009</p>
            <div className="footer-social-icons">
              <a href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></a>
              <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
              <a href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></a>
              <a href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></a>
              <a href="#" aria-label="Discord"><i className="fab fa-discord"></i></a>
            </div>
            <p className="copyright futura">© 2024 AquaNime. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </body>
  );
}