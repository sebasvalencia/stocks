/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1c1915",
        paper: "#f6f1e8",
        rust: "#c45c26",
        moss: "#3d5a45",
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
        display: ["IBM Plex Serif", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
