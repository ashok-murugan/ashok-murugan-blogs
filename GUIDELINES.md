# Blog Content & Structure Guidelines

This document provides detailed guidelines for creating and maintaining blog posts in this repository. To maintain a premium, consistent reading experience, all posts must adhere to these standards.

---

## 1. Directory Structure

Each blog post resides in its own directory named with a descriptive slug.

```text
blog-post-slug/
├── README.md          # Main content
├── TOC.md            # Table of Contents
└── assets/           # Images and media
    ├── banner.png    # Primary banner (Required)
    └── *.png         # Supporting illustrations
```

---

## 2. README.md Standards

### 2.1 Frontmatter
Every `README.md` must start with YAML frontmatter for metadata and SEO.

```yaml
---
title: "Full Title of the Blog"
description: "Compelling 1-2 sentence summary"
author: "Ashok Murugan"
date: "YYYY-MM-DD"
keywords: ["key-topic", "industry", "tech-stack"]
image: "assets/banner.png"
---
```

### 2.2 Branding & Headers
- **Banner:** Start with the banner image centered at 80% width.
- **Section Headers:** Use `##` for main sections and `###` for sub-sections.
- **Clean Headers:** Do not use emojis, icons, or symbols (like 🚀 or 1️⃣) in headers. This ensures reliable anchor generation and professional look.

### 2.3 Introduction & Conclusion
- **Introduction:** Should have a suffix indicating its nature (e.g., `## Introduction — The Uptime Myth`).
- **Conclusion:** Should be a simple `## Conclusion`.

---

## 3. TOC.md Standards (The Navigation Engine)

The `TOC.md` serves as a quick reference for readers and search engines. It must stay perfectly synced with the `README.md`.

### 3.1 Format
1.  **Header:** Always `## Table of Contents`.
2.  **Numbering:** Main sections must be a numbered list (`1.`, `2.`).
3.  **Nesting:** Sub-sections (`###`) should be nested bullet points under their parent section.
4.  **Links:** Must use the `#` anchor format.

### 3.2 GitHub Anchor Link Rules
GitHub generates anchors by:
1.  Converting text to **lowercase**.
2.  Replacing spaces with **hyphens** (`-`).
3.  Removing all **punctuation** (commas, colons, emojis, periods, apostrophes).
4.  Preserving letters and numbers.

**Example:**
- Header: `## 3️⃣ Grant Engineering: Navigating India's Capital Stack` (Old Format)
- Correct Link: `#3-grant-engineering-navigating-indias-capital-stack`
- Header: `## Grant Engineering: Navigating India's Capital Stack` (Clean Format)
- Correct Link: `#grant-engineering-navigating-indias-capital-stack`

---

## 4. Visual Language & Assets

### 4.1 Series Banner Standards (Chalk White + 2 Colors)
- **Unique Series Theme Standard:** Every multi-part technical series (e.g., MCP series, RAG series, System Design series) must maintain a consistent, dedicated color theme across all parts in that series.
- **Base Color:** **Chalk White** (`#f8fafc` / `#ffffff`) to blend cleanly with the blog's reading canvas.
- **Two Complementary Accent Colors:** Each series chooses exactly two signature colors:
  - **MCP Series Standard:** Protocol Electric Blue (`#2563eb`) + Emerald Green (`#059669`).
- **Dimensions & Format:** 16:9 Aspect Ratio (`1200x675` or `1376x768`), high-resolution PNG.
- **Vibe:** Technical, abstract, modular architecture, and minimalist geometry. Avoid stock photography.
- **Zero Embedded Text:** Banners must never contain embedded text titles.

### 4.2 Flow & Architecture Diagrams (Light Theme Invariant)
- **Zero Dark/Black Canvases:** Across the entire blog portal, all flowcharts, sequence diagrams, and architecture maps (`flow` and `arch` diagrams) must use a **clean light design standard** (`#ffffff` canvas). Never use dark slate (`#0f172a`) or black backgrounds, which look harsh against the portal's light reading layout.
- **Card Panels:** Use pure white (`#ffffff`) or subtle pastel-tinted cards (e.g. Sky-50 `#f0f9ff`, Emerald-50 `#f0fdf4`, Indigo-50 `#eef2ff`) with delicate borders (`#cbd5e1`) and 2px rounded corners.
- **Typography:** High-contrast text only. Main titles and node labels in Deep Charcoal (`#0f172a`), secondary/sub-labels in Slate-500 (`#64748b`).
- **No Raw Mermaid Blocks:** Always generate and embed standalone PNG images located in `assets/`.
- **Centering & Scaling:** All diagram images must be wrapped in a centered `<p align="center"><img ... width="85%" /></p>` tag.
- **Reference Code Attachments:** If the post demonstrates a practical systems implementation, attach or link the runnable reference files under `assets/` or link to the project repository for reader hands-on exploration.

### 4.3 Typography & The Portal-Wide RGB Color Standard
The blog portal design system is anchored in a strict, intentional **Red-Green-Blue (RGB)** hierarchy across every section:
- **Red (`var(--line-red)` / `#ef4444`):** Signature accent for key conceptual anchors, bold terms (`strong`), critical system constraints (e.g. `stdout` corruption), and the 1st cycle in TOC/cards. Bold key terms intentionally (15–25 per article) to create sharp visual anchors without visual fatigue.
- **Green (`var(--line-green)` / `#15803d` / `#22c55e`):** Signature accent for technical code tokens (`.prose code`), verified implementations, pre-block left borders, and the 2nd cycle in TOC/cards.
- **Blue (`var(--line-blue)` / `#2563eb` / `#3b82f6`):** Signature accent for hyperlinked resources (`.prose a`), sub-headings (`h3`), blockquote left margins, list markers (`::marker`), and the 3rd cycle in TOC/cards.
- **RGB Gradient Standard:**
  - **Article Title (`h1`):** Red-to-Blue text gradient (`linear-gradient(135deg, var(--line-red), var(--line-blue))`).
  - **Section Dividers (`h2`):** Red-Green-Blue underline border (`linear-gradient(90deg, var(--line-red), var(--line-green), var(--line-blue))`).
  - **Image Outline:** 3px Red-Green-Blue gradient card outline (`linear-gradient(135deg, var(--line-red), var(--line-green), var(--line-blue))`).
- **Balanced Section Composition:** Every section must maintain this balanced triad: Red bold conceptual anchors + Green inline code tokens + Blue reference links, creating high readability and harmonious visual rhythm.

---

## 5. Tone of Voice

### 5.1 The Persona
Write as a **Staff Engineer / Product Founder**. 
- **Analytical:** Show the trade-offs.
- **Truth-seeking:** Don't just follow trends; explain why they work (or don't).
- **Pragmatic:** Focus on results and efficiency.

### 5.2 Stylistic Rules
- **Short Paragraphs:** 2-5 sentences max.
- **Bold for Emphasis:** Use bold for key terms or core insights.
- **Blockquotes:** Use for "Mental Models" or "North Star" quotes.
- **Lists:** Use bullets for features/benefits to improve scannability.

---

## 6. SEO & Metadata

- **Keywords:** Include 5-7 relevant keywords in the frontmatter.
- **Alt Text:** Every image must have descriptive `alt` text for screen readers and SEO.
- **Cross-linking:** When a blog mentions a topic covered in another post, link to that post's `README.md`.

---

## 7. Maintenance Checklist

Before committing a new blog or an edit:
- [ ] No emojis in headers.
- [ ] `TOC.md` links precisely match `README.md` headers.
- [ ] `assets/banner.png` exists and is referenced correctly.
- [ ] Code blocks specify the language for syntax highlighting.
- [ ] Spelling and grammar audit complete.
