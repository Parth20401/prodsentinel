/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--bg-deep)",
        panel: "var(--bg-panel)",
        primary: "var(--accent-primary)",
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
