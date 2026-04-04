/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "media",
  theme: {
    extend: {
      colors: {
        brand: {
          teal: "#008080",
          "teal-dark": "#006666",
          "teal-light": "#33a3a3",
          green: "#32CD32",
          "green-dark": "#28a428",
          "green-light": "#5dd75d",
          orange: "#FF8C00",
          "orange-dark": "#cc7000",
          "orange-light": "#ffad42",
          gold: "#FFD700",
          "gold-dark": "#ccac00",
          "gold-light": "#ffe54d",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        card: "0 2px 8px rgba(0,0,0,0.06)",
        "card-hover": "0 8px 24px rgba(0,0,0,0.1)",
        nav: "0 -2px 12px rgba(0,0,0,0.06)",
      },
    },
  },
  plugins: [],
};
