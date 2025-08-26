import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#0F0F0F",
          secondary: "#1A1A1A",
        },
        foreground: {
          DEFAULT: "#FFFFFF",
          secondary: "#B4B4B4",
          muted: "#6B6B6B",
        },
        primary: {
          DEFAULT: "#FF6B6B",
          hover: "#FF5252",
          light: "#FFE5E5",
        },
        accent: {
          DEFAULT: "#2A2A2A",
          hover: "#333333",
        },
        border: "#333333",
        input: "#2A2A2A",
        ring: "#FF6B6B",
        destructive: "#EF4444",
        muted: {
          DEFAULT: "#1A1A1A",
          foreground: "#6B6B6B",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem", 
        sm: "0.25rem",
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;