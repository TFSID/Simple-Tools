import React from 'react';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';

/**
 * Renders the main home page of the application.
 * This component orchestrates the layout by including the Header,
 * main content area, and Footer.
 */
export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50 text-gray-800">
      {/* Header Component */}
      <Header title="My Next.js App" />

      {/* Main Content Area */}
      <main className="flex-grow container mx-auto p-4 sm:p-6 md:p-8 flex items-center justify-center">
        <section className="bg-white p-8 rounded-lg shadow-xl max-w-2xl w-full text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4 animate-fade-in-down">
            Welcome to Your Next.js Application!
          </h1>
          <p className="text-lg text-gray-700 mb-6 animate-fade-in-up">
            This is a foundational template built with modern best practices,
            type safety, and clean, readable code.
          </p>
          <p className="text-md text-gray-600 mb-8 animate-fade-in-up delay-200">
            Start building amazing things by modifying this page and creating new components.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-md shadow-md
                         hover:bg-blue-700 transition-all duration-300 transform hover:scale-105"
            >
              Get Started
            </button>
            <button
              className="px-8 py-3 bg-gray-200 text-gray-800 font-semibold rounded-md shadow-md
                         hover:bg-gray-300 transition-all duration-300 transform hover:scale-105"
            >
              Learn More
            </button>
          </div>
        </section>
      </main>

      {/* Footer Component */}
      <Footer copyrightText="© 2023 My Next.js App. All rights reserved." />

      {/* Basic global styles for animations (could be in global.css) */}
      <style jsx global>{`
        @keyframes fade-in-down {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-down {
          animation: fade-in-down 0.6s ease-out forwards;
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out forwards;
        }
        .delay-200 {
          animation-delay: 0.2s;
        }
        .delay-400 {
          animation-delay: 0.4s;
        }
      `}</style>
    </div>
  );
}