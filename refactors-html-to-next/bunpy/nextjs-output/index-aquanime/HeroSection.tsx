```typescript
'use client';

import React from 'react';
import Link from 'next/link';

interface HeroSectionProps {
  // Although the original HTML doesn't imply props for this component directly,
  // the interface is provided for adherence to best practices and future extensibility.
}

export default function HeroSection({}: HeroSectionProps) {
  // Note: The dark mode prevention script and global body classes
  // (e.g., 'homepage-body') from the original HTML `<head>` and `<body>`
  // are typically handled in Next.js's `layout.tsx` or `_document.tsx` for optimal
  // performance and flicker prevention, rather than within a client component's `useEffect`.
  // This component focuses on converting the main content structure.

  return (
    <main className="homepage-main-content">
      <section className="hero-section homepage-section content-overlay-1">
        <div className="hero-content animate-target poppins">
          <h1>MULAI PETUALANGAN KREATIFMU</h1>
          <Link href="/community/komunitas_join" passHref legacyBehavior>
            <a className="btn-primary">GABUNG SEKARANG</a>
          </Link>
        </div>
      </section>

      <section className="homepage-section content-overlay-2">
        <div className="hero-content text-left animate-target">
          <h2 className="poppins">
            KOMUNITAS KREATIF JEJEPANGAN<br />BERDOMISILI JABODETABEK & JAWA BARAT
          </h2>
          <p className="futura">
            Kami bikin proyek bareng, belajar bareng, dan berkembang bareng. Kalau kamu suka Budaya Jepang dan kreatif, ya cocok!
          </p>
        </div>
      </section>

      <section className="homepage-section content-overlay-3">
        <div className="container text-center animate-target">
          <h2 className="projects-page-title" style={{ color: 'var(--white)' }} data-lang-key="ideas_come_alive_h2_hp">
            TEMPAT IDE LIAR JADI NYATA
          </h2>
          <div className="projects-grid" style={{ marginTop: '40px' }}>
            <div className="project-card maskot-card">
              <div className="icon"><i className="fas fa-hat-wizard"></i></div>
              <h3 data-lang-key="project_maskot_h3" className="poppins">PROYEK MASKOT</h3>
              <p data-lang-key="project_maskot_p_long" className="futura">
                Mengembangkan maskot komunitas "Aria Ayumi" sebagai wajah komunitas, melalui ilustrasi, cosplay, dan media sosial. Proyek ini terbuka untuk kreator yang ingin berkontribusi dalam visual branding dan storytelling Aria.
              </p>
              <Link href="/proyek/proyek_maskot" passHref legacyBehavior>
                <a className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</a>
              </Link>
            </div>
            <div className="project-card">
              <div className="icon"><i className="fas fa-guitar"></i></div>
              <h3 data-lang-key="project_band_h3" className="poppins">PROYEK BAND</h3>
              <p data-lang-key="project_band_p_long" className="futura">
                Membangun grup band komunitas bergenre J-Pop Rock di region Jawa Barat. Terdiri dari 5 personel: Gitaris, Drummer, Vokalis Gitar, Vokalis Belakang, dan Bassist. Terbuka untuk kolaborasi, latihan, dan perform bareng di event komunitas.
              </p>
              <Link href="/proyek/proyek_band" passHref legacyBehavior>
                <a className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</a>
              </Link>
            </div>
            <div className="project-card">
              <div className="icon"><i className="fas fa-book-open"></i></div>
              <h3 data-lang-key="project_light_novel_h3" className="poppins">PROYEK LIGHT NOVEL</h3>
              <p data-lang-key="project_light_novel_p_long" className="futura">
                Menulis cerita original berbasis maskot "Aria" dan komunitas, menggabungkan proyek visual dan musik ke dalam satu universe. Genre utama: Slice of Life, Drama, dan Musik. Bisa jadi IP komunitas yang berkembang bersama.
              </p>
              <Link href="/proyek/proyek_light_novel" passHref legacyBehavior>
                <a className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</a>
              </Link>
            </div>
            <div className="project-card">
              <div className="icon"><i className="fas fa-newspaper"></i></div>
              <h3 data-lang-key="project_journalism_h3" className="poppins">PROYEK JURNALISTIK</h3>
              <p data-lang-key="project_journalism_p_long" className="futura">
                Mengemas riset dan berita seputar anime & budaya Jejepangan dalam format video dan artikel. Diedarkan lewat media sosial AquaNime. Terbuka bagi penulis, editor, dan video creator yang ingin berbagi insight.
              </p>
              <Link href="/proyek/proyek_jurnalistik" passHref legacyBehavior>
                <a className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</a>
              </Link>
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <Link href="/pages/proyek" passHref legacyBehavior>
              <a className="btn-secondary">LIHAT SEMUA PROYEK</a>
            </Link>
          </div>
        </div>
      </section>

      <section className="homepage-section content-overlay-4">
        <div className="container text-center animate-target">
          <h2 style={{ color: 'var(--white)' }} className="poppins">
            DARI KOMUNITAS BIASA,<br />JADI TEMPAT BERKEMBANGN LUAR BIASA
          </h2>
          <p style={{ color: 'var(--white)' }} className="futura">
            Komunitas ini lebih dari sekadar kumpul-kumpul ini tentang perjalanan dan transformasi bareng teman-teman yang sepemikiran.
          </p>

          {/* Testimonial slider commented out as per original HTML.
              If activated, ensure images use paths relative to the /public directory,
              e.g., src="/assets/images/member1.png".
          */}
          {/* <div className="testimonial-slider-container">
            <div className="testimonial-slider">
              <div className="testimonial-item">
                <img src="/assets/images/member1.png" alt="member 1" className="testimonial-avatar" loading="lazy" />
                <p className="futura">"Bergabung dengan AquaNime adalah salah satu keputusan terbaik saya! Saya menemukan banyak teman baru dan bisa mengembangkan bakat saya di sini."</p>
                <h4>- Nama Member 1</h4>
                <span>Divisi Kreatif</span>
              </div>
              <div className="testimonial-item">
                <img src="/assets/images/member2.png" alt="member 2" className="testimonial-avatar" loading="lazy" />
                <p className="futura">"Dukungan yang saya dapatkan dari komunitas ini luar biasa. Ide-ide saya tidak pernah dianggap aneh, justru selalu didukung untuk berkembang."</p>
                <h4>- Nama Member 2</h4>
                <span>Regional Bandung</span>
              </div>
              <div className="testimonial-item">
                <img src="/assets/images/member3.png" alt="member 3" className="testimonial-avatar" loading="lazy" />
                <p className="futura">"Sering ada event dan kolaborasi seru. AquaNime bukan hanya komunitas, tapi keluarga yang selalu ada untuk saling belajar."</p>
                <h4>- Nama Member 3</h4>
                <span>Proyek Band</span>
              </div>
              <div className="testimonial-item">
                <img src="/assets/images/member4.png" alt="member 4" className="testimonial-avatar" loading="lazy" />
                <p className="futura">"Dari cuma suka-suka anime, sekarang saya jadi bisa nulis light novel berkat bimbingan dari para senior di sini."</p>
                <h4>- Nama Member 4</h4>
                <span>Divisi Konten</span>
              </div>
            </div>
            <button className="slider-button prev-button"><i className="fas fa-chevron-left"></i></button>
            <button className="slider-button next-button"><i className="fas fa-chevron-right"></i></button>
            <div className="slider-dots"></div>
          </div> */}
        </div>
      </section>

      <section className="homepage-section content-overlay-1">
        <div className="container text-center animate-target">
          <h2 className="poppins">MEDIA & PARTNER<br />YANG SUDAH BERKOLABORASI DENGAN AQUANIME</h2>
          <div className="partners-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
            <div className="partner-logo"><img src="/assets/images/atx_logo.png" alt="ATX Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/manekineko_logo.png" alt="Karaoke Manekineko Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/rri_logo.png" alt="RRI Jakarta 105.0 FM Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/suara_com_logo.png" alt="Suara.com Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/yoursay_id_logo.png" alt="Yoursay.id Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/oronamin_c_logo.png" alt="Oronamin C Drink Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/bstation_logo.png" alt="Bstation Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/aok_logo.png" alt="AOK Logo" loading="lazy" /></div>
            <div className="partner-logo"><img src="/assets/images/jagat_logo.png" alt="Jagat Logo" loading="lazy" /></div>
          </div>
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <p style={{ color: 'var(--white)' }} data-lang-key="want_to_be_partner_p" className="futura">
              Mau jadi partner kami juga?
            </p>
            <Link href="/pages/kontak" passHref legacyBehavior>
              <a className="btn-secondary poppins" data-lang-key="contact_now_btn">HUBUNGI SEKARANG</a>
            </Link>
          </div>
        </div>
      </section>

      <section className="homepage-section content-overlay-2">
        <div className="container text-center animate-target">
          <h2 className="poppins">BERANI TUNJUKKAN İMAJINASI KAMU?</h2>
          <p className="futura">
            Di AquaNime, kreativitas kamu nggak akan dianggap aneh. Bikin, kolaborasi, dan wujudkan passion bareng komunitas yang ngertiin kamu.
          </p>
          <div className="cta-buttons">
            {/* Corrected duplicate className attribute */}
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
  );
}
```