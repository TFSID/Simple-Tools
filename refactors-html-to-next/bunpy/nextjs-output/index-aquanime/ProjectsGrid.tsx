```typescript
// components/ProjectsGrid.tsx
'use client';

import React from 'react';

// Define props interface for a single Project Card
interface ProjectCardProps {
  iconClass: string;
  title: string;
  description: string;
  link: string;
  linkText: string;
  dataLangKeyTitle?: string;
  dataLangKeyDescription?: string;
}

// Reusable ProjectCard sub-component
const ProjectCard: React.FC<ProjectCardProps> = ({
  iconClass,
  title,
  description,
  link,
  linkText,
  dataLangKeyTitle,
  dataLangKeyDescription,
}) => {
  return (
    <div className="project-card bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg flex flex-col items-center text-center transition-all duration-300 hover:shadow-xl hover:scale-[1.02] transform">
      <div className="icon text-4xl text-blue-600 dark:text-blue-400 mb-4">
        <i className={iconClass}></i>
      </div>
      <h3 className="poppins text-xl font-semibold mb-2" data-lang-key={dataLangKeyTitle}>
        {title}
      </h3>
      <p className="futura text-gray-600 dark:text-gray-300 mb-4 flex-grow">
        {description}
      </p>
      <a href={link} className="btn-primary inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300" data-lang-key="learn_more_project">
        {linkText}
      </a>
    </div>
  );
};

// Main ProjectsGrid component
const ProjectsGrid: React.FC = () => {
  return (
    <section className="homepage-section content-overlay-3 py-16 md:py-24 bg-gray-100 dark:bg-gray-900">
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center animate-target">
        <h2 className="projects-page-title text-3xl md:text-4xl font-bold mb-10 poppins" style={{ color: 'var(--white)' }} data-lang-key="ideas_come_alive_h2_hp">
          TEMPAT IDE LIAR JADI NYATA
        </h2>
        <div className="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-10">
          <ProjectCard
            iconClass="fas fa-hat-wizard"
            title="PROYEK MASKOT"
            description="Mengembangkan maskot komunitas 'Aria Ayumi' sebagai wajah komunitas, melalui ilustrasi, cosplay, dan media sosial. Proyek ini terbuka untuk kreator yang ingin berkontribusi dalam visual branding dan storytelling Aria."
            link="proyek/proyek_maskot.html"
            linkText="Selengkapnya"
            dataLangKeyTitle="project_maskot_h3"
            dataLangKeyDescription="project_maskot_p_long"
          />
          <ProjectCard
            iconClass="fas fa-guitar"
            title="PROYEK BAND"
            description="Membangun grup band komunitas bergenre J-Pop Rock di region Jawa Barat. Terdiri dari 5 personel: Gitaris, Drummer, Vokalis Gitar, Vokalis Belakang, dan Bassist. Terbuka untuk kolaborasi, latihan, dan perform bareng di event komunitas."
            link="proyek/proyek_band.html"
            linkText="Selengkapnya"
            dataLangKeyTitle="project_band_h3"
            dataLangKeyDescription="project_band_p_long"
          />
          <ProjectCard
            iconClass="fas fa-book-open"
            title="PROYEK LIGHT NOVEL"
            description="Menulis cerita original berbasis maskot 'Aria' dan komunitas, menggabungkan proyek visual dan musik ke dalam satu universe. Genre utama: Slice of Life, Drama, dan Musik. Bisa jadi IP komunitas yang berkembang bersama."
            link="proyek/proyek_light_novel.html"
            linkText="Selengkapnya"
            dataLangKeyTitle="project_light_novel_h3"
            dataLangKeyDescription="project_light_novel_p_long"
          />
          <ProjectCard
            iconClass="fas fa-newspaper"
            title="PROYEK JURNALISTIK"
            description="Mengemas riset dan berita seputar anime & budaya Jejepangan dalam format video dan artikel. Diedarkan lewat media sosial AquaNime. Terbuka bagi penulis, editor, dan video creator yang ingin berbagi insight."
            link="proyek/proyek_jurnalistik.html"
            linkText="Selengkapnya"
            dataLangKeyTitle="project_journalism_h3"
            dataLangKeyDescription="project_journalism_p_long"
          />
        </div>
        <div className="text-center mt-10">
          <a href="pages/proyek.html" className="btn-secondary inline-block border border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white dark:hover:bg-blue-400 dark:hover:text-white font-bold py-2 px-4 rounded transition duration-300 poppins">
            LIHAT SEMUA PROYEK
          </a>
        </div>
      </div>
    </section>
  );
};

export default ProjectsGrid;
```