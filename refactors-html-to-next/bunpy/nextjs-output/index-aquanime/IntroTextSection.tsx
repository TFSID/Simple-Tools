```typescript
'use client';

import Image from 'next/image';
import Link from 'next/link';
import { Poppins } from 'next/font/google';

// Poppins font setup
const poppins = Poppins({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'], // Adjust weights as needed for your design
  variable: '--font-poppins', // Use CSS variable for global application or specific elements
  display: 'swap',
});

// Futura Std 4 is not a Google Font. It would typically be loaded via next/font/local
// or as an external <link> in app/layout.tsx. For this example, we'll assume it's
// handled globally by a CSS import, and apply 'futura' as a className.

// Global styles (styles.css, Bootstrap, Font Awesome, other fonts) and the
// dark mode preload script should be handled in `app/layout.tsx` for Next.js App Router
// or `pages/_document.tsx` for Pages Router, not within a client component.
// The dark mode script in particular needs to run before React hydration to prevent FOUC.

interface IntroTextSectionProps {
  // If this component were to receive dynamic data or interact with a parent,
  // props would be defined here. For this static content, no specific props are needed.
}

const IntroTextSection: React.FC<IntroTextSectionProps> = () => {
  return (
    // The 'homepage-body' class typically applies to the <body> tag.
    // Here, we apply it to the outermost div of the component.
    // We also apply the Poppins font variable and a generic 'font-sans' fallback.
    <div className={`homepage-body ${poppins.variable} font-sans`}>
      <header>
        <nav>
          <div className="logo">
            {/* Replace <img> with next/image. Add appropriate width and height. */}
            <Image src="/assets/images/logo.png" alt="AquaNime Logo" width={50} height={50} loading="lazy" />
            <span>AquaNime</span>
          </div>
          <ul id="nav-links" className={poppins.className}>
            {/* Replace <a> with next/link for internal navigation. Adjust paths for App Router. */}
            <li><Link href="/">BERANDA</Link></li>
            <li><Link href="/tentang">TENTANG</Link></li>
            <li><Link href="/proyek">PROYEK</Link></li>
            <li><Link href="/portal">PORTAL</Link></li>
            <li><Link href="/kontak">KONTAK</Link></li>
          </ul>
          <div className={`lang-mode-toggles ${poppins.className}`}>
            <div className="dark-mode-toggle" id="dark-mode-toggle">
              {/* Font Awesome icons are typically available if linked in layout.tsx */}
              <i className="fas fa-moon"></i> <span>Dark Mode</span>
            </div>
          </div>
          <div className="social-icons">
            <Link href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></Link>
            <Link href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></Link>
            <Link href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></Link>
            <Link href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></Link>
            <Link href="#" aria-label="Discord"><i className="fab fa-discord"></i></Link>
          </div>
          <div className="hamburger-menu" id="sidebar">
            <i className="fas fa-bars"></i>
          </div>
        </nav>
      </header>

      <main className="homepage-main-content">
        <section className="hero-section homepage-section content-overlay-1">
          <div className={`hero-content animate-target ${poppins.className}`}>
            <h1 className="">MULAI PETUALANGAN KREATIFMU</h1>
            <Link href="/community/komunitas_join" className="btn-primary">GABUNG SEKARANG</Link>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="hero-content text-left animate-target">
            <h2 className={poppins.className}>KOMUNITAS KREATIF JEJEPANGAN<br />BERDOMISILI JABODETABEK & JAWA BARAT</h2>
            <p className="futura">Kami bikin proyek bareng, belajar bareng, dan berkembang bareng. Kalau kamu suka Budaya Jepang dan kreatif, ya cocok!</p>
          </div>
        </section>

        <section className="homepage-section content-overlay-3">
          <div className="container text-center animate-target">
            <h2 className="projects-page-title" style={{ color: 'var(--white)' }} data-lang-key="ideas_come_alive_h2_hp">TEMPAT IDE LIAR JADI NYATA</h2>
            <div className="projects-grid" style={{ marginTop: '40px' }}>
              <div className="project-card maskot-card">
                <div className="icon"><i className="fas fa-hat-wizard"></i></div>
                <h3 data-lang-key="project_maskot_h3" className={poppins.className}>PROYEK MASKOT</h3>
                <p data-lang-key="project_maskot_p_long" className="futura">Mengembangkan maskot komunitas "Aria Ayumi" sebagai wajah komunitas, melalui ilustrasi, cosplay, dan media sosial. Proyek ini terbuka untuk kreator yang ingin berkontribusi dalam visual branding dan storytelling Aria.</p>
                <Link href="/proyek/proyek_maskot" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
              <div className="project-card">
                <div className="icon"><i className="fas fa-guitar"></i></div>
                <h3 data-lang-key="project_band_h3" className={poppins.className}>PROYEK BAND</h3>
                <p data-lang-key="project_band_p_long" className="futura">Membangun grup band komunitas bergenre J-Pop Rock di region Jawa Barat. Terdiri dari 5 personel: Gitaris, Drummer, Vokalis Gitar, Vokalis Belakang, dan Bassist. Terbuka untuk kolaborasi, latihan, dan perform bareng di event komunitas.</p>
                <Link href="/proyek/proyek_band" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
              <div className="project-card">
                <div className="icon"><i className="fas fa-book-open"></i></div>
                <h3 data-lang-key="project_light_novel_h3" className={poppins.className}>PROYEK LIGHT NOVEL</h3>
                <p data-lang-key="project_light_novel_p_long" className="futura">Menulis cerita original berbasis maskot "Aria" dan komunitas, menggabungkan proyek visual dan musik ke dalam satu universe. Genre utama: Slice of Life, Drama, dan Musik. Bisa jadi IP komunitas yang berkembang bersama.</p>
                <Link href="/proyek/proyek_light_novel" className="btn-primary" data-lang-key="learn_more_project">Selengkapnya</Link>
              </div>
              <div className="project-card">
                <div className="icon"><i className="fas fa-newspaper"></i></div>
                <h3 data-lang-key="project_journalism_h3" className={poppins.className}>PROYEK JURNALISTIK</h3>
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
            <h2 style={{ color: 'var(--white)' }} className={poppins.className}>DARI KOMUNITAS BIASA,<br />JADI TEMPAT BERKEMBANGN LUAR BIASA</h2>
            <p style={{ color: 'var(--white)' }} className="futura">Komunitas ini lebih dari sekadar kumpul-kumpul ini tentang perjalanan dan transformasi bareng teman-teman yang sepemikiran.</p>

            {/* Testimonial slider section (commented out in original HTML, kept as JSX comment) */}
            {/*
            <div className="testimonial-slider-container">
              <div className="testimonial-slider">
                <div className="testimonial-item">
                  <Image src="/assets/images/member1.png" alt="member 1" className="testimonial-avatar" width={80} height={80} loading="lazy" />
                  <p className="futura">"Bergabung dengan AquaNime adalah salah satu keputusan terbaik saya! Saya menemukan banyak teman baru dan bisa mengembangkan bakat saya di sini."</p>
                  <h4>- Nama Member 1</h4>
                  <span>Divisi Kreatif</span>
                </div>
                <div className="testimonial-item">
                  <Image src="/assets/images/member2.png" alt="member 2" className="testimonial-avatar" width={80} height={80} loading="lazy" />
                  <p className="futura">"Dukungan yang saya dapatkan dari komunitas ini luar biasa. Ide-ide saya tidak pernah dianggap aneh, justru selalu didukung untuk berkembang."</p>
                  <h4>- Nama Member 2</h4>
                  <span>Regional Bandung</span>
                </div>
                <div className="testimonial-item">
                  <Image src="/assets/images/member3.png" alt="member 3" className="testimonial-avatar" width={80} height={80} loading="lazy" />
                  <p className="futura">"Sering ada event dan kolaborasi seru. AquaNime bukan hanya komunitas, tapi keluarga yang selalu ada untuk saling belajar."</p>
                  <h4>- Nama Member 3</h4>
                  <span>Proyek Band</span>
                </div>
                <div className="testimonial-item">
                  <Image src="/assets/images/member4.png" alt="member 4" className="testimonial-avatar" width={80} height={80} loading="lazy" />
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
            <h2 className={poppins.className}>MEDIA & PARTNER<br />YANG SUDAH BERKOLABORASI DENGAN AQUANIME</h2>
            <div className="partners-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
              <div className="partner-logo"><Image src="/assets/images/atx_logo.png" alt="ATX Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/manekineko_logo.png" alt="Karaoke Manekineko Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/rri_logo.png" alt="RRI Jakarta 105.0 FM Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/suara_com_logo.png" alt="Suara.com Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/yoursay_id_logo.png" alt="Yoursay.id Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/oronamin_c_logo.png" alt="Oronamin C Drink Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/bstation_logo.png" alt="Bstation Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/aok_logo.png" alt="AOK Logo" width={120} height={60} loading="lazy" /></div>
              <div className="partner-logo"><Image src="/assets/images/jagat_logo.png" alt="Jagat Logo" width={120} height={60} loading="lazy" /></div>
            </div>
            <div style={{ textAlign: 'center', marginTop: '40px' }}>
              <p style={{ color: 'var(--white)' }} data-lang-key="want_to_be_partner_p" className="futura">Mau jadi partner kami juga?</p>
              <Link href="/kontak" className={`btn-secondary ${poppins.className}`} data-lang-key="contact_now_btn">HUBUNGI SEKARANG</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-2">
          <div className="container text-center animate-target">
            <h2 className={poppins.className}>BERANI TUNJUKKAN IMAJINASI KAMU?</h2>
            <p className="futura">Di AquaNime, kreativitas kamu nggak akan dianggap aneh. Bikin, kolaborasi, dan wujudkan passion bareng komunitas yang ngertiin kamu.</p>
            <div className="cta-buttons">
              {/* Corrected redundant className attribute */}
              <Link href="#" className={`btn-secondary ${poppins.className}`}>MULAI BERKARYA</Link>
              <Link href="#" className={`btn-secondary ${poppins.className}`}>GABUNG KOMUNITAS</Link>
            </div>
          </div>
        </section>

        <section className="homepage-section content-overlay-3">
          <div className="container text-center animate-target">
            <h2 className={poppins.className}>LIHAT AKTIVITAS KAMI<br />LEBIH DEKAT DI SOSIAL MEDIA</h2>
            <div className={`large-social-icons futura`}>
              <Link href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></Link>
              <Link href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></Link>
              <Link href="#" aria-label="TikTok"><i className="fab fa-tiktok"></i></Link>
              <Link href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></Link>
              <Link href="#" aria-label="Discord"><i className="fab fa-discord"></i></Link>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-content">
          <div className="footer-section">
            <h4 className={poppins.className}>EKSPLORASI</h4>
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
            <h4 className={poppins.className}>KOMUNITAS</h4>
            <ul className="futura">
              <li><Link href="/community/komunitas_join">Join Komunitas</Link></li>
              <li><Link href="/community/komunitas_divisi_regional">Divisi & Regional</Link></li>
              <li><Link href="/community/komunitas_karya_member">Karya Member</Link></li>
              <li><Link href="/community/komunitas_forum_diskusi">Forum Diskusi</Link></li> {/* Completed the truncated list item */}
            </ul>
          </div>
          {/* Add other footer sections here if they exist in the full original HTML */}
        </div>
        {/* Add more footer content if available in the original */}
      </footer>
    </div>
  );
};

export default IntroTextSection;
```