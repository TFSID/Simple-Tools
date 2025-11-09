```tsx
import Header from '@/components/Header';
import Navbar from '@/components/Navbar';
import Logo from '@/components/Logo';
import NavLinks from '@/components/NavLinks';
import LangModeToggles from '@/components/LangModeToggles';
import DarkModeToggle from '@/components/DarkModeToggle';
import SocialIcons from '@/components/SocialIcons';
import HamburgerMenu from '@/components/HamburgerMenu';
import MainContent from '@/components/MainContent';
import HeroSection from '@/components/HeroSection';
import HeroContentBlock from '@/components/HeroContentBlock';
import PrimaryButton from '@/components/PrimaryButton';
import IntroTextSection from '@/components/IntroTextSection';
import ProjectsShowcaseSection from '@/components/ProjectsShowcaseSection';
import SectionHeading from '@/components/SectionHeading';
import ProjectsGrid from '@/components/ProjectsGrid';
import ProjectCard from '@/components/ProjectCard';
import ProjectCardIcon from '@/components/ProjectCardIcon';
import ProjectCardTitle from '@/components/ProjectCardTitle';
import SecondaryButton from '@/components/SecondaryButton';
import TestimonialsSection from '@/components/TestimonialsSection';
import TestimonialSliderContainer from '@/components/TestimonialSliderContainer';
import TestimonialItem from '@/components/TestimonialItem';
import SliderButton from '@/components/SliderButton';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-50">
      <Header>
        <Navbar>
          <Logo text="MyBrand" />
          <div className="hidden md:flex items-center space-x-4">
            <NavLinks links={[{ href: '/', label: 'Home' }, { href: '/projects', label: 'Projects' }, { href: '/about', label: 'About' }, { href: '/contact', label: 'Contact' }]} />
            <LangModeToggles currentLang="en" />
            <DarkModeToggle />
            <SocialIcons />
          </div>
          <HamburgerMenu>
            <NavLinks links={[{ href: '/', label: 'Home' }, { href: '/projects', label: 'Projects' }, { href: '/about', label: 'About' }, { href: '/contact', label: 'Contact' }]} isMobile />
            <div className="flex justify-center p-4 space-x-4">
              <LangModeToggles currentLang="en" />
              <DarkModeToggle />
            </div>
            <div className="flex justify-center p-4">
              <SocialIcons />
            </div>
          </HamburgerMenu>
        </Navbar>
      </Header>

      <MainContent>
        <HeroSection backgroundImage="/images/hero-bg.jpg">
          <HeroContentBlock
            title="Your Vision, Our Expertise"
            description="We build exceptional digital experiences that drive growth and connect with your audience."
          >
            <PrimaryButton href="/contact">Get Started</PrimaryButton>
          </HeroContentBlock>
        </HeroSection>

        <IntroTextSection
          title="Innovate. Create. Inspire."
          text="At MyBrand, we believe in crafting solutions that are not just functional but truly inspire. Our team of dedicated professionals works tirelessly to bring your ideas to life with precision and creativity, ensuring every project is a masterpiece."
        />

        <ProjectsShowcaseSection>
          <SectionHeading title="Our Recent Work" subtitle="See what we've been building" />
          <ProjectsGrid>
            <ProjectCard href="/project/1">
              <ProjectCardIcon icon="/icons/design.svg" alt="Design Icon" />
              <ProjectCardTitle>Creative Web Design</ProjectCardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">Crafting stunning and user-friendly interfaces.</p>
            </ProjectCard>
            <ProjectCard href="/project/2">
              <ProjectCardIcon icon="/icons/dev.svg" alt="Development Icon" />
              <ProjectCardTitle>Robust App Development</ProjectCardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">Building scalable and performant mobile applications.</p>
            </ProjectCard>
            <ProjectCard href="/project/3">
              <ProjectCardIcon icon="/icons/seo.svg" alt="SEO Icon" />
              <ProjectCardTitle>Strategic SEO Optimization</ProjectCardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">Enhancing online visibility and organic reach.</p>
            </ProjectCard>
          </ProjectsGrid>
          <div className="mt-12 text-center">
            <SecondaryButton href="/projects">View All Projects</SecondaryButton>
          </div>
        </ProjectsShowcaseSection>

        <TestimonialsSection>
          <SectionHeading title="What Our Clients Say" subtitle="Trusted by businesses worldwide" />
          <TestimonialSliderContainer>
            <TestimonialItem
              quote="MyBrand transformed our online presence. Their attention to detail and commitment to excellence were truly remarkable!"
              author="Jane Doe"
              position="CEO, Tech Innovations"
              avatar="/images/avatar-jane.jpg"
            />
            <TestimonialItem
              quote="Working with MyBrand was a fantastic experience. They delivered on time and exceeded our expectations with their innovative solutions."
              author="John Smith"
              position="Founder, Creative Solutions"
              avatar="/images/avatar-john.jpg"
            />
            {/* You would typically pass props to determine current slide and total */}
            <SliderButton direction="prev" />
            <SliderButton direction="next" />
          </TestimonialSliderContainer>
        </TestimonialsSection>
      </MainContent>
    </div>
  );
}
```