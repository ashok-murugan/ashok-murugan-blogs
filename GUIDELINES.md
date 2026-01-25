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

### 4.1 Banner Style
- **Dimensions:** 16:9 Aspect Ratio.
- **Vibe:** Technical, abstract, minimalist. Avoid generic stock photos.
- **No Text:** Banners should not contain embedded text.

### 4.2 Technical Diagrams
- **Consistency:** Use consistent line weights and color palettes (e.g., muted blues, grays, and blacks).
- **Format:** PNG is preferred for diagrams to ensure crispness on all displays.
- **Centering:** All images must be wrapped in a centered `<p>` tag with `width="80%"`.

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
