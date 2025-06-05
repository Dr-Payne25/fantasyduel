/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sleeper: {
          primary: '#01A2E8',
          secondary: '#FA3958',
          dark: '#0A0E1A',
          darker: '#080B14',
          gray: '#1A1F2E',
          light: '#E8E9ED'
        }
      }
    },
  },
  plugins: [],
}