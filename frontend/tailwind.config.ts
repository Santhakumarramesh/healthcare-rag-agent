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
        // CareCopilot AI Design System (from Stitch designs)
        primary: "#000666",
        "primary-container": "#1a237e",
        "primary-fixed": "#e0e0ff",
        "primary-fixed-dim": "#bdc2ff",
        "on-primary": "#ffffff",
        "on-primary-container": "#8690ee",
        "on-primary-fixed": "#000767",
        "on-primary-fixed-variant": "#343d96",
        "inverse-primary": "#bdc2ff",
        "surface-tint": "#4c56af",

        secondary: "#0061a4",
        "secondary-container": "#33a0fd",
        "secondary-fixed": "#d1e4ff",
        "secondary-fixed-dim": "#9ecaff",
        "on-secondary": "#ffffff",
        "on-secondary-container": "#00355c",
        "on-secondary-fixed": "#001d36",
        "on-secondary-fixed-variant": "#00497d",

        tertiary: "#00201d",
        "tertiary-container": "#003733",
        "tertiary-fixed": "#8ef4e9",
        "tertiary-fixed-dim": "#71d7cd",
        "on-tertiary": "#ffffff",
        "on-tertiary-container": "#3ca89e",
        "on-tertiary-fixed": "#00201d",
        "on-tertiary-fixed-variant": "#00504a",

        surface: "#f7f9fc",
        "surface-dim": "#d8dadd",
        "surface-bright": "#f7f9fc",
        "surface-variant": "#e0e3e6",
        "surface-container": "#eceef1",
        "surface-container-low": "#f2f4f7",
        "surface-container-lowest": "#ffffff",
        "surface-container-high": "#e6e8eb",
        "surface-container-highest": "#e0e3e6",
        "on-surface": "#191c1e",
        "on-surface-variant": "#454652",
        "inverse-surface": "#2d3133",
        "inverse-on-surface": "#eff1f4",

        background: "#f7f9fc",
        "on-background": "#191c1e",

        error: "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error": "#ffffff",
        "on-error-container": "#93000a",

        outline: "#767683",
        "outline-variant": "#c6c5d4",
      },
      fontFamily: {
        headline: ["Manrope", "sans-serif"],
        body: ["Inter", "sans-serif"],
        label: ["Inter", "sans-serif"],
        sans: ["Inter", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        full: "9999px",
      },
      boxShadow: {
        card: "0 4px 12px rgba(0,0,0,0.03)",
        "card-md": "0 8px 24px rgba(0,0,0,0.06)",
        "card-lg": "0 16px 48px rgba(0,0,0,0.08)",
      },
      backgroundImage: {
        mesh: "radial-gradient(at 0% 0%, #e0e0ff 0, transparent 50%), radial-gradient(at 100% 0%, #d1e4ff 0, transparent 50%)",
      },
    },
  },
  plugins: [],
};

export default config;
