/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      // Modern web3 spacing scale
      spacing: {
        'xs': '0.5rem',    // 8px
        'sm': '0.75rem',   // 12px
        'md': '1rem',      // 16px
        'lg': '1.25rem',   // 20px
        'xl': '1.5rem',    // 24px
        '2xl': '2rem',     // 32px
        '3xl': '2.5rem',   // 40px
        '4xl': '3rem',     // 48px
      },
      // Button and component sizing
      fontSize: {
        'btn-sm': ['0.75rem', { lineHeight: '1rem' }],    // 12px
        'btn-md': ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        'btn-lg': ['1rem', { lineHeight: '1.5rem' }],      // 16px
        'btn-xl': ['1.125rem', { lineHeight: '1.75rem' }], // 18px
      },
      // Modern web3 border radius
      borderRadius: {
        'sm': '0.375rem',  // 6px
        'md': '0.5rem',    // 8px
        'lg': '0.75rem',   // 12px
        'xl': '1rem',      // 16px
        '2xl': '1.5rem',   // 24px
      },
      // Component heights for consistent sizing
      height: {
        'btn-sm': '2rem',     // 32px
        'btn-md': '2.5rem',   // 40px
        'btn-lg': '3rem',     // 48px
        'btn-xl': '3.5rem',   // 56px
        'input-sm': '2rem',   // 32px
        'input-md': '2.5rem', // 40px
        'input-lg': '3rem',   // 48px
      },
      // Modern web3 shadows
      boxShadow: {
        'btn': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'btn-hover': '0 4px 12px rgba(0, 0, 0, 0.15)',
        'btn-active': '0 1px 2px rgba(0, 0, 0, 0.1)',
        'card': '0 4px 6px rgba(0, 0, 0, 0.05)',
        'card-hover': '0 8px 25px rgba(0, 0, 0, 0.15)',
      }
    },
  },
  plugins: [],
}
