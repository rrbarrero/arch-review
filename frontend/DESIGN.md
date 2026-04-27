---
version: alpha
name: Arch Review Console
description: A restrained operational interface for reviewing technical systems with retrieved evidence.
colors:
  primary: "#0F4C5C"
  primary-hover: "#0B3D4A"
  secondary: "#2F5D62"
  accent: "#B86B3F"
  background: "#F6F8F9"
  surface: "#FFFFFF"
  surface-muted: "#EEF3F5"
  border: "#D6E0E3"
  text: "#102027"
  text-muted: "#5E6E73"
  success: "#1F7A5C"
  warning: "#B86B3F"
  danger: "#B23B3B"
typography:
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: 0
  title-sm:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: 0
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: 0
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: 560
    lineHeight: 1.2
    letterSpacing: 0
  code-sm:
    fontFamily: Geist Mono
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: 0
rounded:
  sm: 4px
  md: 6px
  lg: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    height: 36px
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
---

# Arch Review Console

## Overview

Arch Review Console is a work-focused interface for engineers inspecting uploaded source and infrastructure context. It should feel calm, precise, and trustworthy: closer to an observability console than a marketing app. Information density is welcome when it improves scanning, but every panel should retain enough whitespace to avoid visual fatigue.

## Colors

The palette uses cool operational neutrals with a deep teal primary and one warm accent for attention. Primary teal marks the main action and selected state. The warm accent is reserved for warnings, chunk counts, and secondary emphasis.

## Typography

Use Geist for interface text and Geist Mono for file extensions, code, counts, and source-like metadata. Headings stay compact. Letter spacing remains `0` across the interface.

## Layout

The product is a two-pane console. The ingestion pane is fixed and scannable, while the chat pane gets the majority of the viewport. Use an 8px spacing rhythm, with 16px as the default panel padding and 24px only for larger empty states.

## Elevation & Depth

Depth is conveyed through borders, tonal backgrounds, and modest shadows. Avoid glossy gradients and oversized decorative effects. Interactive focus should be visible through the primary ring color.

## Shapes

Use a restrained 4-8px radius. Buttons, inputs, cards, message bubbles, and upload surfaces should share the same squared technical language.

## Components

Buttons are compact and icon-led when the action is clear. Cards are used for framed tools and repeated metrics only. Status chips use borders plus subtle fills. Code labels use the mono font and muted surface backgrounds.

## Do's and Don'ts

- Do prioritize scanning, source review, and repeated use over visual drama.
- Do reserve the primary color for main actions and active states.
- Do use warm accent sparingly for warnings or counts.
- Don't use decorative gradients as the main identity.
- Don't nest decorative cards inside cards.
- Don't let chips, buttons, or metric tiles resize unexpectedly.
