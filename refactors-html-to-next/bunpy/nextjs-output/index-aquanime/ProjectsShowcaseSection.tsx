```typescript
'use client';

import React from 'react';

interface ProjectsShowcaseSectionProps {
  // Define any props this component might receive.
  // For this conversion, the component is self-contained without dynamic props,
  // but a prop interface is included as per best practices.
}

const ProjectsShowcaseSection: React.FC<ProjectsShowcaseSectionProps> = () => {
  return (
    <section className="homepage-section content-overlay-3">
      <div className="container text-center animate-target">
        <h2 className="projects-page-title poppins" style={{ color: 'var(--white)' }} data-lang-key="ideas_come_alive_h2_hp">
          TEMPAT IDE LIAR JADI NYATA
        </h2>
        <div className="projects-grid" style={{ marginTop: '40px' }}>
          <div className="project-card maskot-card">
            <div className="icon">
              <i className="fas fa-hat-wizard"></i>
            </div>
            <h3 data-lang-key="project_maskot_h3" className="poppins">PROYEK MASKOT</h3>
            <p data-lang-key="project_maskot_p_long" className="futura">
              Mengembangkan maskot komunitas "Aria Ayumi" sebagai wajah komunitas, melalui ilustrasi, cosplay, dan media sosial. Proyek ini terbuka untuk kreator yang ingin berkontribusi dalam visual branding dan storytelling Aria.
            </p>
            <a href="proyek/proyek_maskot.html" className="btn-primary" data-lang-key="learn_more_project">
              Selengkapnya
            </a>
          </div>
          <div className="project-card">
            <div className="icon">
              <i className="fas fa-guitar"></i>
            </div>
            <h3 data-lang-key="project_band_h3" className="poppins">PROYEK BAND</h3>
            <p data-lang-key="project_band_p_long" className="futura">
              Membangun grup band komunitas bergenre J-Pop Rock di region Jawa Barat. Terdiri dari 5 personel: Gitaris, Drummer, Vokalis Gitar, Vokalis Belakang, dan Bassist. Terbuka untuk kolaborasi, latihan, dan perform bareng di event komunitas.
            </p>
            <a href="proyek/proyek_band.html" className="btn-primary" data-lang-key="learn_more_project">
              Selengkapnya
            </a>
          </div>
          <div className="project-card">
            <div className="icon">
              <i className="fas fa-book-open"></i>
            </div>
            <h3 data-lang-key="project_light_novel_h3" className="poppins">PROYEK LIGHT NOVEL</h3>
            <p data-lang-key="project_light_novel_p_long" className="futura">
              Menulis cerita original berbasis maskot "Aria" dan komunitas, menggabungkan proyek visual dan musik ke dalam satu universe. Genre utama: Slice of Life, Drama, dan Musik. Bisa jadi IP komunitas yang berkembang bersama.
            </p>
            <a href="proyek/proyek_light_novel.html" className="btn-primary" data-lang-key="learn_more_project">
              Selengkapnya
            </a>
          </div>
          <div className="project-card">
            <div className="icon">
              <i className="fas fa-newspaper"></i>
            </div>
            <h3 data-lang-key="project_journalism_h3" className="poppins">PROYEK JURNALISTIK</h3>
            <p data-lang-key="project_journalism_p_long" className="futura">
              Mengemas riset dan berita seputar anime & budaya Jejepangan dalam format video dan artikel. Diedarkan lewat media sosial AquaNime. Terbuka bagi penulis, editor, dan video creator yang ingin berbagi insight.
            </p>
            <a href="proyek/proyek_jurnalistik.html" className="btn-primary" data-lang-key="learn_more_project">
              Selengkapnya
            </a>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: '40px' }}>
          <a href="pages/proyek.html" className="btn-secondary">
            LIHAT SEMUA PROYEK
          </a>
        </div>
      </div>
    </section>
  );
};

export default ProjectsShowcaseSection;
```