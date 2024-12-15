# URL to Podcast Converter - Design System Documentation

## Brand Typography

### Primary Font
- **Font Family**: Geist Sans
- **Fallback Stack**: system-ui, -apple-system, sans-serif
- **Usage**: Primary typeface for all interface elements

### Type Scale
```css
/* Headers */
h1: 24px (text-2xl)  - Bold, leading-tight
h2: 20px (text-xl)   - Bold, leading-tight
h3: 18px (text-lg)   - Bold, leading-tight
h4: 16px (text-base) - Bold, leading-tight
h5: 16px (text-base) - Semibold, leading-tight
h6: 16px (text-base) - Medium, leading-tight

/* Body */
Base: 16px (text-base) - Regular, leading-relaxed
```

## Color System

### Light Theme Colors
```css
Background:    HSL(0, 0%, 100%)    /* Pure white */
Foreground:    HSL(0, 0%, 3.9%)    /* Near black */
Primary:       HSL(0, 0%, 9%)      /* Dark gray */
Secondary:     HSL(0, 0%, 96.1%)   /* Light gray */
Muted:         HSL(0, 0%, 96.1%)   /* Light gray */
Accent:        HSL(0, 0%, 96.1%)   /* Light gray */
Destructive:   HSL(0, 84.2%, 60.2%)/* Red */
Border:        HSL(0, 0%, 89.8%)   /* Medium gray */
```

### Dark Theme Colors
```css
Background:    HSL(0, 0%, 3.9%)    /* Near black */
Foreground:    HSL(0, 0%, 98%)     /* Off white */
Primary:       HSL(0, 0%, 98%)     /* Off white */
Secondary:     HSL(0, 0%, 14.9%)   /* Dark gray */
Muted:         HSL(0, 0%, 14.9%)   /* Dark gray */
Accent:        HSL(0, 0%, 14.9%)   /* Dark gray */
Destructive:   HSL(0, 62.8%, 30.6%)/* Dark red */
Border:        HSL(0, 0%, 14.9%)   /* Dark gray */
```

### Chart Colors
#### Light Theme
1. HSL(12, 76%, 61%)   - Coral
2. HSL(173, 58%, 39%)  - Teal
3. HSL(197, 37%, 24%)  - Dark Blue
4. HSL(43, 74%, 66%)   - Gold
5. HSL(27, 87%, 67%)   - Orange

#### Dark Theme
1. HSL(220, 70%, 50%)  - Blue
2. HSL(160, 60%, 45%)  - Green
3. HSL(30, 80%, 55%)   - Orange
4. HSL(280, 65%, 60%)  - Purple
5. HSL(340, 75%, 55%)  - Pink

## Component Styling

### Border Radius
```css
Large:   8px  (var(--radius))
Medium:  6px  (calc(var(--radius) - 2px))
Small:   4px  (calc(var(--radius) - 4px))
```

### Spacing System
Follows Tailwind's default spacing scale:
- 0: 0px
- 1: 0.25rem (4px)
- 2: 0.5rem (8px)
- 3: 0.75rem (12px)
- 4: 1rem (16px)
- 6: 1.5rem (24px)
- 8: 2rem (32px)

## Animations

### Float Animation
Used for hover effects and emphasizing interactive elements
```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
Duration: 2s
Timing: ease-in-out
Iteration: infinite
```

### Slow Pulse Animation
Used for loading states and progress indicators
```css
@keyframes slowPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
Duration: 2s
Timing: cubic-bezier(0.4, 0, 0.6, 1)
Iteration: infinite
```

## UI Components

### Buttons
- Primary: Solid background with white text
- Secondary: Light gray background with dark text
- Disabled: Reduced opacity (0.5)
- Hover: Slight darkness adjustment
- Active: Slight scale reduction

### Input Fields
- Default: Light border (HSL(0, 0%, 89.8%))
- Focus: Dark border with ring effect
- Error: Destructive color border
- Disabled: Reduced opacity background

### Cards
- Background: White (light) / Near black (dark)
- Border: Light gray (light) / Dark gray (dark)
- Shadow: Subtle elevation
- Radius: var(--radius) (8px)

### Progress Indicators
Four-stage process visualization:
1. URL Processing (Link icon)
2. Content Extraction (File icon)
3. Audio Generation (Headphones icon)
4. Podcast Feed (Podcast icon)

Each stage features:
- Icon transition effects
- Color changes for active/complete states
- Pulse animation for loading state

## Layout Guidelines

### Spacing
- Component padding: 1.5rem (24px)
- Inter-component margin: 1rem (16px)
- Content width: max-w-md (28rem/448px)
- Vertical rhythm: Based on 4px grid

### Container Widths
- Small: max-w-sm (24rem/384px)
- Medium: max-w-md (28rem/448px)
- Large: max-w-lg (32rem/512px)

### Responsive Breakpoints
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- 2xl: 1536px

## Accessibility Guidelines

### Color Contrast
- Text on background: Minimum 4.5:1
- Large text on background: Minimum 3:1
- Interactive elements: Minimum 3:1

### Focus States
- Visible focus rings on interactive elements
- High contrast focus indicators
- No focus suppression

### Motion
- Respect reduced-motion preferences
- Keep animations subtle and purposeful
- Provide static alternatives where needed

