---
name: Synthetic Intelligence Interface
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#b9cacb'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#849495'
  outline-variant: '#3a494b'
  surface-tint: '#00dbe7'
  primary: '#e1fdff'
  on-primary: '#00363a'
  primary-container: '#00f2ff'
  on-primary-container: '#006a71'
  inverse-primary: '#00696f'
  secondary: '#dcb8ff'
  on-secondary: '#480081'
  secondary-container: '#7701d0'
  on-secondary-container: '#dcb7ff'
  tertiary: '#e0fdff'
  on-tertiary: '#0e3639'
  tertiary-container: '#bbe2e5'
  on-tertiary-container: '#416669'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#74f5ff'
  primary-fixed-dim: '#00dbe7'
  on-primary-fixed: '#002022'
  on-primary-fixed-variant: '#004f54'
  secondary-fixed: '#efdbff'
  secondary-fixed-dim: '#dcb8ff'
  on-secondary-fixed: '#2c0051'
  on-secondary-fixed-variant: '#6700b5'
  tertiary-fixed: '#c3eaed'
  tertiary-fixed-dim: '#a7cdd1'
  on-tertiary-fixed: '#002022'
  on-tertiary-fixed-variant: '#274c4f'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-xl:
    fontFamily: Geist
    fontSize: 72px
    fontWeight: '200'
    lineHeight: 80px
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '400'
    lineHeight: 32px
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '300'
    lineHeight: 24px
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1440px
  gutter: 24px
---

## Brand & Style

The design system is defined by a sense of **Hyper-Intelligence and Immersive Clarity**. It draws inspiration from cinematic "heads-up displays" but strips away the visual clutter of traditional sci-fi interfaces to prioritize high usability and focus. The brand personality is calm, precise, and anticipatory.

The aesthetic follows a **Minimalist-Glassmorphic** approach. It utilizes deep-space voids to create an infinite canvas where UI elements appear as floating, translucent shards of data. The emotional response should be one of "effortless power"—the user should feel like they are interacting with a sophisticated, sentient entity that is both advanced and approachable.

**Visual Pillars:**
- **Holographic Depth:** Use of multi-layered transparency and backdrop blurs to simulate physical volume.
- **Luminous Precision:** High-contrast accents (Cyan/Violet) against dark backgrounds to draw attention to active intelligence.
- **Fluid Vitality:** Elements do not just "appear"; they materialize through organic motion, suggesting the AI is always "breathing" and active.

## Colors

The palette is rooted in the **Deep Space Black (#050505)**, which serves as the infinite foundation. This is not a flat black, but a vacuum that allows light-based elements to pop.

- **Primary (Electric Cyan):** Used for primary actions, system status, and active voice waveforms. It represents the "logic" of the AI.
- **Secondary (Neon Violet):** Used for ambient intelligence states, suggestions, and tertiary decorative depth. It represents the "intuition" and "personality" of the AI.
- **Accents:** Tertiary "Deep Teal" is used for low-priority container backgrounds to maintain a monochromatic hierarchy without losing the futuristic tint.
- **Glass Surfaces:** Surfaces are never opaque. They use a variable alpha (3% to 8%) to create the glassmorphic stacking effect.

## Typography

Typography in this design system emphasizes technical precision and modern elegance. 

- **Primary Typeface (Geist):** Selected for its ultra-clean, Swiss-inspired geometry. It feels mechanical yet legible. Use lighter weights (200-300) for large display text to evoke a "holographic" feel.
- **Technical Typeface (JetBrains Mono):** Used for metadata, system status, timestamps, and data readouts. This reinforces the "AI" nature of the product, suggesting the underlying code and logic.
- **Scaling:** Headlines should be large and airy. Body text remains tight and legible. Letter spacing is slightly increased for labels to ensure readability against glowing backgrounds.

## Layout & Spacing

The layout philosophy is **Center-Out Centric**, mirroring a cockpit or HUD. While a fluid grid is used for content organization, the primary focal point is often the center of the screen where voice interaction and ambient AI visualizations reside.

- **Grid Model:** A 12-column fluid grid for desktop with 24px gutters. On mobile, this collapses to a single column with 16px margins.
- **Safe Zones:** High-priority "glanceable" information is kept in the corners (system time, battery, connection) to leave the central "Stage" open for primary tasks.
- **Spacing Rhythm:** Based on an 8px linear scale. Large vertical gaps (48px+) are used between distinct logical sections to maintain the minimalist "uncluttered" aesthetic.

## Elevation & Depth

Depth is not communicated through shadows, but through **Luminous Layering and Refraction**.

- **Backdrop Blurs:** Every floating panel must use a `backdrop-filter: blur(24px)` to separate it from the "Deep Space" background.
- **Inner Glows:** Instead of drop shadows, active elements use a subtle 1px inner border with a 50% opacity primary color and a 4px outer bloom (glow) to simulate light emission.
- **Z-Axis Stacking:** 
    - **Level 0 (Background):** Pure #050505.
    - **Level 1 (Sub-surface):** Low-opacity gradients, subtle grain.
    - **Level 2 (Panels):** Glassmorphic containers with 1px stroke.
    - **Level 3 (Interactions/Modals):** Heightened glow and increased stroke weight.

## Shapes

The shape language is **Technical-Organic**. It avoids the extreme playfulness of fully circular "bubbly" UI while rejecting the aggression of sharp 90-degree corners.

- **Standard Radius:** Elements use a 0.5rem (8px) radius for a modern, balanced feel. 
- **Large Containers:** Use 1rem (16px) for main dashboard cards to emphasize the "glass slab" metaphor.
- **Interactive Triggers:** Buttons and chips use the "Rounded" level to feel distinct from structural panels.
- **The Orb:** The AI voice visualization is the only perfectly circular element, signifying its role as the "soul" of the interface.

## Components

### Voice Orb (Primary Component)
A central, fluid visualization that reacts to audio input. It should use a mix of Cyan and Violet gradients with a "Gooey" filter effect to feel like liquid light.

### Glass Cards
Translucent containers with a top-down linear gradient (10% white to 0% white). All cards must have a 1px border using the `border_color_hex` token to define the edge against the dark background.

### Neon Buttons
- **Default:** Transparent background, primary color 1px border, "Label-Mono" typography.
- **Hover/Active:** Background fills with a 10% primary color tint, and the border glow intensity doubles.

### Status Chips
Small, mono-spaced tags used for "Processing," "Listening," or "Syncing." They feature a small "pulse" dot to the left of the text to indicate life.

### Input Fields
Minimalist underlines instead of full boxes. When focused, the underline expands into a thin luminous bar that spans the width of the container.

### Data Micro-Visuals
Small sparklines and telemetry data should be rendered in the secondary color (Violet) to provide background context without distracting from the primary task.