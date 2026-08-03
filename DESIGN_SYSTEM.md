# CyberGuard SOC Design System & UX Standards

## 1. Design Philosophy
CyberGuard is designed to emulate modern tier-1 Security Operations Center (SOC) platforms (CrowdStrike Falcon, Microsoft Sentinel, Splunk ES, Google Chronicle). It prioritizes **high-contrast dark mode**, **glassmorphism**, **clear visual hierarchy**, and **instant threat visibility**.

---

## 2. Color Palette & UI Tokens

| Token Name | Hex Code | Purpose |
| :--- | :--- | :--- |
| **SOC Dark Canvas** | `#090d16` | Main application background |
| **Sidebar Canvas** | `#0d1322` | Primary navigation sidebar |
| **Glass Card Background** | `rgba(18, 24, 41, 0.85)` | Glassmorphic KPI cards & containers |
| **Accent Glow Blue** | `#38bdf8` | Primary active elements & metrics |
| **Critical Severity Red** | `#dc2626` / `#7f1d1d` | Critical threat alerts & badges |
| **High Severity Orange** | `#ea580c` / `#991b1b` | High severity incidents |
| **Medium Severity Yellow**| `#eab308` / `#854d0e` | Warning indicators |
| **Success / Low Green** | `#10b981` / `#14532d` | Normal authentications & low risk |

---

## 3. Typography & Spacing System
- **Heading Font**: `Outfit`, sans-serif (800 weight for Brand, 700 for Section titles).
- **Body Font**: `Inter`, system-ui, sans-serif (400 for text, 600 for tables/badges).
- **Code / Monospace**: `Fira Code`, `JetBrains Mono` for IP addresses, Usernames, and SQL queries.
- **Card Padding**: 16px padding with 12px border radius and subtle 1px border.

---

## 4. Accessibility & Micro-Interactions
- **Contrast Ratios**: All text tokens achieve WCAG AAA contrast ratio on dark background (`#090d16`).
- **Interactive Feedback**: KPI cards feature smooth transform translations on hover (`translateY(-2px)`).
- **Status Badges**: Severity levels feature color-coded background fills and text labels to avoid reliance solely on color perception.
