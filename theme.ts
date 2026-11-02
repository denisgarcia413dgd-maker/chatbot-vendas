import { useMemo } from "react";
import { Appearance, StyleSheet, useColorScheme } from "react-native";

export type ColorScheme = "light" | "dark";

// Configuração obrigatória seguindo o "7 Dark-First Utility"
const dark = {
  surface: "#0B0D10",           // Fundo principal escuro
  onSurface: "#F1F3F5",         // Texto principal claro
  surfaceSecondary: "#15181E",  // Cartões e linhas
  onSurfaceSecondary: "#C1C8D3",
  surfaceTertiary: "#1D2129",   // Container de Inputs e Logs do Terminal
  onSurfaceTertiary: "#A0A8B6",
  surfaceInverse: "#E2E8F0",
  onSurfaceInverse: "#0B0D10",
  muted: "#7E8899",

  // Cores de marca (Base Laranja/Amber conforme regras da Shopee/Mercado Livre unificadas no estilo tático)
  brand: "#EE4D2D",
  onBrand: "#FFFFFF",
  brandPrimary: "#EE4D2D",
  onBrandPrimary: "#FFFFFF",
  brandSecondary: "#FF7B54",
  onBrandSecondary: "#1A0804",
  brandTertiary: "#3B1C16",     // Ideal para fundos de avatares com letras proeminentes
  onBrandTertiary: "#FFB098",

  success: "#22C55E",
  onSuccess: "#052E16",
  warning: "#EAB308",
  onWarning: "#422006",
  error: "#EF4444",
  onError: "#450A0A",
  info: "#14B8A6",              // Tom Teal substituto de azuis/roxos permitidos
  onInfo: "#042F2E",

  border: "#262A33",
  borderStrong: "#3A404D",
  divider: "#1F232B",
};

export type ThemeColors = typeof dark;
export const defaultScheme = "dark" satisfies ColorScheme;
export const themes: { light: ThemeColors; dark: ThemeColors } = { light: dark, dark: dark };

export function useTheme() {
  return { scheme: "dark" as ColorScheme, colors: dark };
}

export function makeStyles<T extends StyleSheet.NamedStyles<T>>(
  factory: (colors: ThemeColors) => T,
): () => T {
  return function useStyles(): T {
    return useMemo(() => StyleSheet.create(factory(dark)), []);
  };
}
