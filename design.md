# HeatShield AI --- Product & Visual Design Specification

**Document:** `design.md`\
**Version:** 1.0\
**Status:** Design direction approved for implementation\
**Product:** HeatShield AI\
**Tagline:** Intelligence Against Extreme Heat. Protection for Every
Worker.

------------------------------------------------------------------------

## 1. Product vision

HeatShield AI is an occupational heat-safety intelligence platform. It
combines environmental weather observations with a worker's reported
work conditions to produce a transparent screening assessment and
practical safety guidance.

The interface must communicate three things immediately:

1.  **What are the current environmental conditions?**
2.  **What worker and worksite factors were reported?**
3.  **What should the worker or supervisor do next, and what information
    is still missing?**

This is a safety-oriented product, not a generic AI chatbot and not a
decorative analytics dashboard.

### Primary design principle

**Clarity before decoration. Action before analytics. Trust before AI
spectacle.**

The interface should feel like a calm, professional climate-operations
product: precise, humane, accessible, and dependable.

------------------------------------------------------------------------

## 2. Current UI diagnosis

The current screen looks like an unstyled HTML form rather than a
finished product. The main issues visible in the supplied screenshot
are:

-   There is no visual hierarchy between the brand, page title, form,
    and results.
-   Form labels, controls, and values run together, making fields
    difficult to scan.
-   The form is presented as one dense horizontal block instead of
    logical groups.
-   The primary action does not stand out.
-   There is no clear page grid, spacing rhythm, card system, or
    consistent alignment.
-   The black background and default-looking text do not communicate a
    deliberate visual system.
-   The empty result area has no useful structure or explanation of what
    will appear.
-   There is no persistent context showing the selected location or
    assessment state.
-   The emergency/safety disclaimer is visually weak despite being
    important.
-   The page does not yet communicate the distinction between weather
    observations and a worksite occupational assessment.

The redesign must solve these structural problems before adding visual
effects.

------------------------------------------------------------------------

## 3. Users and key jobs

### Outdoor worker

Needs to understand the immediate guidance in simple language, ideally
in their preferred language, with minimal technical terminology.

### Site supervisor

Needs to review reported worker conditions, missing information,
recommended controls, and emergency actions.

### Safety officer

Needs transparent inputs, source information, assessment limitations,
and a clear distinction between environmental observations and validated
occupational measurements.

### Primary user journey

1.  Open the dashboard.
2.  Confirm or enter the worksite location.
3.  Enter worker and exposure information.
4.  Submit an assessment.
5.  Review environmental observations.
6.  Review exposure factors and missing information.
7.  Read practical controls and safety advisory.
8.  Take action or collect missing data.

Do not make users navigate through multiple pages to complete this core
journey.

------------------------------------------------------------------------

## 4. Information architecture

Use a desktop application shell with a compact left sidebar and a main
content area.

### Primary navigation

-   **Overview** --- current conditions, latest assessment, priority
    actions.
-   **New assessment** --- worker and worksite information form.
-   **Assessments** --- previous assessments, when persistence is
    implemented.
-   **Safety guidance** --- validated guidance and emergency protocol.
-   **Resources** --- cooling and hydration resources, when implemented.
-   **Settings** --- language, units, account and preferences, when
    implemented.

Only show navigation destinations that exist. Unimplemented sections
should be marked as planned or omitted; do not create fake pages.

### Main overview layout

``` text
┌──────────────────────────────────────────────────────────────────────┐
│ TOP BAR: HeatShield AI / location / data source / profile            │
├───────────────┬──────────────────────────────────────────────────────┤
│               │ PAGE TITLE                                           │
│ SIDEBAR       │ Overview                                             │
│               │ Short explanation + New assessment action            │
│ Overview      ├──────────────────────────────────────────────────────┤
│ New assessment│ ENVIRONMENTAL CONDITIONS                              │
│ Assessments   │ Temperature | Humidity | Feels like | Wind            │
│ Safety guide  ├───────────────────────────────────┬──────────────────┤
│ Resources     │ WEATHER TREND                     │ ASSESSMENT STATUS│
│               │ Hourly forecast chart             │ Status + missing │
│               │                                   │ information      │
│               ├───────────────────────────────────┴──────────────────┤
│               │ LATEST WORKER ASSESSMENT                              │
│               │ Workload | Sunlight | Shade | Water | Acclimatization│
│               ├──────────────────────────────────────────────────────┤
│               │ PRIORITY ACTIONS                                     │
│               │ Clear, actionable safety recommendations             │
└───────────────┴──────────────────────────────────────────────────────┘
```

### New assessment page

The assessment form should be a focused workflow, not a long
unstructured form.

Use a two-column desktop layout:

-   Left: form sections, approximately 60--65% width.
-   Right: sticky assessment context panel, approximately 35--40% width.

Form sections:

1.  **Worksite** --- location, work area.
2.  **Worker profile** --- occupation, workload, shift duration,
    acclimatization.
3.  **Environmental exposure** --- direct sunlight, shade availability.
4.  **Safety provisions** --- water access, PPE.
5.  **Exposure and recovery** --- continuous exposure duration, break
    frequency.

Use clear field labels above controls. Never put labels and inputs on
the same line without spacing.

### Assessment results page or result state

Present results in this order:

1.  Assessment status and timestamp.
2.  Environmental observations and source.
3.  Worker profile summary.
4.  Exposure factors.
5.  Missing information.
6.  Recommended controls.
7.  Safety advisory.
8.  Limitations and emergency guidance.

The most actionable information must appear before long AI-generated
narrative text.

------------------------------------------------------------------------

## 5. Visual direction

### Design concept: Climate Operations

A restrained, high-clarity interface inspired by professional
environmental monitoring and modern B2B software.

Avoid: - Generic AI neon gradients. - Excessive glassmorphism. - Huge
decorative blobs. - Glowing borders on every card. - Tiny low-contrast
labels. - Excessive rounded pills. - Dense tables as the only way to
communicate worker status. - Fake live indicators or fabricated
readings.

Use: - Deep ink/navy surfaces. - Warm off-white primary text. - Muted
slate secondary text. - Teal as the primary action and data accent. -
Amber for caution and incomplete information. - Red only for genuine
emergency or critical states. - Thin, subtle borders. - Consistent
spacing and alignment. - Large, readable metric values.

### Color tokens

Use CSS variables so the theme can be changed centrally.

  Token                Suggested value   Usage
  -------------------- ----------------- -----------------------------------
  `--background`       `#0B1220`         Application background
  `--surface`          `#111C2E`         Sidebar and primary cards
  `--surface-raised`   `#17243A`         Elevated panels and inputs
  `--surface-muted`    `#1C2B42`         Hover and subtle grouping
  `--border`           `#29384F`         Card and control borders
  `--text-primary`     `#F3F6FA`         Main text
  `--text-secondary`   `#A7B4C7`         Supporting text
  `--text-muted`       `#78879D`         Metadata only
  `--accent`           `#35C6B0`         Primary action and key highlights
  `--accent-hover`     `#27A994`         Hover state
  `--info`             `#67B7F7`         Informational data
  `--warning`          `#F2B85B`         Incomplete or caution states
  `--danger`           `#F07171`         Emergency states only
  `--success`          `#58C995`         Confirmed success

Color must never be the only way to communicate status. Pair it with
text and an icon.

### Typography

Use **Inter** or a similar highly legible sans-serif.

Suggested type scale:

  Element           Desktop size     Weight
  --------------- -------------- ----------
  Page title           28--32 px   650--700
  Section title        18--20 px        600
  Card title           14--16 px        600
  Metric value         30--36 px        650
  Body                 14--16 px        400
  Labels               12--13 px        500
  Metadata                 12 px        400

Use sentence case. Avoid all-caps labels except small section overlines.

### Spacing and shape

-   Base spacing unit: 4 px.
-   Common gaps: 8, 12, 16, 24, 32 px.
-   Card padding: 20--24 px.
-   Page gutter: 32 px desktop; 20 px tablet; 16 px mobile.
-   Card radius: 12--16 px.
-   Input radius: 8--10 px.
-   Buttons: 10 px radius.
-   Borders: 1 px solid tokenized border.
-   Shadows: subtle and used sparingly.

------------------------------------------------------------------------

## 6. Component specifications

### Application shell

-   Sidebar width: 240--256 px expanded, 72 px collapsed.
-   Top bar height: 64--72 px.
-   Main content max width: approximately 1440 px.
-   Keep navigation labels and icons aligned.
-   Show active navigation with a subtle tinted background and accent
    indicator.
-   On mobile, replace the sidebar with a menu/drawer.

### Metric cards

Each environmental metric card contains:

-   Small icon and label.
-   Large numeric value.
-   Unit.
-   Optional short context.
-   Data timestamp/source available in a details area.

Example layout:

``` text
┌──────────────────────────────┐
│ ◉  AIR TEMPERATURE           │
│                              │
│ 25.9 °C                      │
│ Current observation          │
│                              │
│ Open-Meteo · 02:15            │
└──────────────────────────────┘
```

Do not add invented thresholds or risk labels to these cards.

### Assessment status

Use explicit states:

-   **Ready** --- required input is available.
-   **Processing** --- assessment is running.
-   **Incomplete** --- required or important information is missing.
-   **Screening only** --- screening completed without validated
    worksite WBGT.
-   **Error** --- request failed; provide a retry action.

Do not label a worker "safe," "high risk," or "low risk" unless a
validated assessment methodology supports that classification.

### Form controls

-   Labels above controls.
-   Required/optional status visible.
-   Help text beneath fields where needed.
-   Full keyboard accessibility.
-   Visible focus rings.
-   Select controls with consistent height.
-   Use segmented controls for short binary choices where clear.
-   Use checkboxes for PPE selections.
-   Preserve values after API errors.
-   Validate numeric ranges before submission.
-   Show field-level validation messages.

### Primary action

Use one visually dominant action:

**Run heat assessment**

During submission: - Disable duplicate submission. - Show spinner and
"Analyzing conditions..." label. - Keep the page stable. - Provide a
clear error state if the API fails.

### Results and advisory panels

Use separate sections for: - Environmental observations. - Worker
exposure factors. - Missing information. - Recommended controls. -
Safety advisory. - Assessment limitations.

Do not combine all information into one large text box.

------------------------------------------------------------------------

## 7. Data integrity and safety UX

This is a safety-related product. The UI must preserve the meaning of
backend data.

### Weather data

-   Display the source and observation time.
-   Identify readings as environmental observations.
-   Distinguish current observations from forecast values.
-   Never describe apparent temperature as WBGT.
-   Do not imply a weather station is measuring the exact worksite.

### Worker information

-   Show reported information as reported, not independently verified.
-   Distinguish `false` from `unknown` and `not provided`.
-   Never silently convert missing values into defaults that imply
    certainty.
-   Preserve the difference between continuous exposure duration and
    break frequency.

### Assessment status

-   Show `incomplete` prominently when information is missing.
-   Explain exactly what is missing.
-   Do not hide limitations below the fold.
-   Do not create a numerical risk score from unvalidated inputs.

### Emergency guidance

If the product receives or displays signs such as confusion, seizures,
collapse, or loss of consciousness, the interface must show an
unmistakable emergency message directing users to seek immediate
emergency medical assistance.

Do not route an emergency through the normal AI assessment flow or imply
that an AI response should delay emergency care.

### AI-generated content

-   Clearly identify AI-generated narrative.
-   Keep deterministic facts visually distinguishable from
    model-generated explanation.
-   Do not let an LLM override validated structured values.
-   Avoid presenting generated advice as a substitute for occupational
    safety professionals.

------------------------------------------------------------------------

## 8. Interaction and motion

Motion should help explain state changes, not decorate the interface.

-   Hover transitions: 120--180 ms.
-   Drawer and modal transitions: 180--220 ms.
-   Use subtle loading skeletons for data panels.
-   Avoid animated counters that make measurements appear to change
    artificially.
-   Respect `prefers-reduced-motion`.
-   Never use flashing or pulsing emergency indicators.

Loading states should communicate what is happening: 1. Retrieving
weather observations. 2. Analyzing environmental conditions. 3.
Evaluating worker exposure. 4. Preparing safety advisory.

Only show these stages if they correspond to actual backend progress.
Otherwise use a neutral processing state.

------------------------------------------------------------------------

## 9. Responsive behavior

### Desktop: 1280 px and above

-   Expanded sidebar.
-   Four metric cards in one row when space allows.
-   Two-column content panels.
-   Sticky context panel on assessment form.

### Tablet: 768--1279 px

-   Collapsible sidebar.
-   Two metric cards per row.
-   Stack lower dashboard panels as needed.
-   Form may become a single column.

### Mobile: below 768 px

-   Sidebar becomes a drawer.
-   One metric card per row on narrow screens.
-   Full-width form controls and primary action.
-   Stack assessment sections vertically.
-   Keep emergency guidance visible and readable.
-   Avoid horizontal scrolling.

------------------------------------------------------------------------

## 10. Accessibility requirements

Target WCAG 2.2 AA where practical.

-   Body text contrast ratio at least 4.5:1.
-   Large text contrast ratio at least 3:1.
-   Keyboard-operable navigation, forms, dialogs and controls.
-   Visible focus states.
-   Semantic headings and landmarks.
-   Explicit labels for every input.
-   Accessible error announcements.
-   Screen-reader-friendly status updates.
-   Do not rely on color alone.
-   Touch targets preferably at least 44 × 44 px.
-   Charts must include a text summary or accessible data alternative.

------------------------------------------------------------------------

## 11. Frontend implementation guidance

### Recommended stack

-   Next.js App Router.
-   TypeScript.
-   Tailwind CSS.
-   Lucide React.
-   Recharts for forecast visualizations.
-   Reusable components with clear props.
-   Native `fetch` or a small typed API client.

### Suggested component structure

``` text
frontend/src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   └── assessments/
│       └── new/
│           └── page.tsx
│
├── components/
│   ├── layout/
│   │   ├── app-shell.tsx
│   │   ├── sidebar.tsx
│   │   └── topbar.tsx
│   │
│   ├── dashboard/
│   │   ├── page-header.tsx
│   │   ├── metric-card.tsx
│   │   ├── weather-overview.tsx
│   │   ├── forecast-chart.tsx
│   │   └── assessment-status.tsx
│   │
│   ├── assessment/
│   │   ├── worker-form.tsx
│   │   ├── worker-summary.tsx
│   │   ├── exposure-factors.tsx
│   │   └── missing-information.tsx
│   │
│   ├── advisory/
│   │   ├── safety-advisory.tsx
│   │   ├── recommended-controls.tsx
│   │   └── emergency-banner.tsx
│   │
│   └── ui/
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── select.tsx
│       └── badge.tsx
│
└── lib/
    ├── api.ts
    ├── types.ts
    └── utils.ts
```

### API integration

Use a configurable backend URL:

``` env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The frontend should call:

``` http
POST /api/v1/assess
```

with the validated request schema expected by FastAPI.

Implementation requirements:

-   Define TypeScript request and response types.
-   Handle loading, success, validation and server-error states.
-   Preserve backend assessment status and limitations.
-   Do not fabricate fallback weather values.
-   Do not substitute mock results when the API fails.
-   Configure CORS on FastAPI for the local frontend origin.
-   Before deployment, use the actual deployed backend URL and
    appropriate environment configuration.

------------------------------------------------------------------------

## 12. Definition of done

The redesign is complete when:

-   [ ] The page has a consistent application shell and navigation.
-   [ ] Typography, spacing, colors and card styles use shared design
    tokens.
-   [ ] Worker form is grouped into understandable sections.
-   [ ] All labels and controls are aligned and accessible.
-   [ ] The primary action is visually clear.
-   [ ] Loading and API error states are implemented.
-   [ ] Real backend data populates the dashboard.
-   [ ] Forecast values are clearly distinguished from current
    observations.
-   [ ] Missing information is visible and understandable.
-   [ ] Safety recommendations are separated from environmental data.
-   [ ] Assessment limitations are visible.
-   [ ] Emergency guidance is unmistakable.
-   [ ] Layout works on desktop, tablet and mobile.
-   [ ] No fabricated readings, scores or completed features appear.
-   [ ] The interface passes a keyboard and contrast review.

------------------------------------------------------------------------

## 13. Final design standard

HeatShield AI should look and behave like a serious climate-safety
operations product.

The interface must not try to impress users with visual effects. It must
earn trust through hierarchy, readability, accurate data presentation,
transparent limitations and clear actions.

**The user should understand the environmental conditions, the worker's
reported exposure, what is missing, and what action to take within
seconds.**

That is the standard for every screen and component.
