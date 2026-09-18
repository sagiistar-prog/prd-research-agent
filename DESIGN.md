---
name: PRD Review
description: A source-annotated reading and review interface for an offline PRD artifact.
colors:
  ground: "#f1f3f7"
  paper: "#fff"
  ink: "#212936"
  muted: "#596577"
  line: "#d8dfe8"
  blue: "#264fb6"
  selected: "#e9effc"
  focus: "#174bbd"
typography:
  headline:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "-.02em"
  section:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "21px"
    fontWeight: 700
    lineHeight: 1.5
  title:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.6
  body:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.7
  note:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  control: "8px"
  field: "6px"
spacing:
  compact: "6px"
  small: "8px"
  control-inset: "12px"
  standard: "16px"
  detail: "18px"
  mobile-inset: "20px"
  section: "24px"
  generous: "28px"
  heading: "32px"
  separation: "48px"
components:
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.paper}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  source-reference:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.blue}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "6px 12px"
  text-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "8px 12px"
  navigation:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  navigation-current:
    backgroundColor: "{colors.selected}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  feature-row:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    padding: "24px 0"
  evidence-record:
    textColor: "{colors.ink}"
    padding: "22px 12px"
  evidence-record-highlight:
    backgroundColor: "{colors.selected}"
    textColor: "{colors.ink}"
    padding: "22px 12px"
---

# Design System: PRD Review

## Overview

**Creative North Star: "Source-annotated review brief"**

The implemented interface uses a cool gray workspace, a white reading plane, and blue actions. Its character comes from readable Chinese text, visible reasoning, fine dividers, and native disclosure rows. Review controls stay close to the content they affect.

This is a scan of the generic review renderer, not a visual identity for a fictional example product. The built HTML, CSS, and JavaScript are the visual authority; there is no approved image comp. The implemented palette is gray and blue. The broader palette preference did not result in a purple token.

**Key Characteristics:**

- Flat surfaces separated by tone and thin rules.
- A compact type hierarchy with generous line height for continuous reading.
- Plain metadata and source buttons within unboxed content rows.
- Native inputs and disclosures with visible keyboard focus.
- Content visible immediately, with restrained color transitions.

Source authority: `assets/review/index.html`, `assets/review/style.css`, `assets/review/review.js`, and `scripts/review_renderer.py`. Desktop, mobile, and the corrected contextual return were inspected in `.impeccable/review/`. This records the current implementation; it does not claim broader browser, assistive-technology, or print acceptance. The sidecar's synthesized tonal ramps are panel previews, not additional shipped colors.

## Colors

Cool neutrals carry the reading hierarchy. Blue identifies actions, selection, and focus.

### Primary

- **Review blue** (`blue`): primary download action, links, source references, disclosure labels, and field carets.
- **Selection wash** (`selected`): active navigation and the currently traced evidence record.
- **Keyboard focus blue** (`focus`): a visible outline around the element receiving keyboard focus.

### Neutral

- **Workspace gray** (`ground`): the outer page and navigation region.
- **Reading white** (`paper`): the main reading surface and resting controls.
- **Reading ink** (`ink`): main text and headings.
- **Supporting slate** (`muted`): objective text, labels, counts, and notes.
- **Divider gray** (`line`): control borders and structural rules.

**The Action Color Rule.** Keep blue attached to a meaningful action, selection, or focus state. The interface does not assign arbitrary colors to feature priorities.

Interaction-specific border and state colors remain literal CSS in the sidecar snippets. They are not expanded into a speculative palette.

## Typography

**Body and interface font:** the system stack in the frontmatter. The implementation loads no web font and uses the same stack for headings, controls, quotations, and raw source text.

The hierarchy is compact. Weight and spacing provide emphasis without a separate display treatment.

- **Headline:** product name. At the mobile breakpoint its size becomes (24px), with its existing line height and tracking preserved.
- **Section:** panel heading.
- **Title:** feature, planning block, or evidence identifier.
- **Body:** rationale, quotations, buttons, input values, and acceptance text.
- **Label:** supporting descriptions, filter labels, count, and source actions.
- **Note:** footer and navigation note; feature metadata uses this size with its own slate color.

The brand and active navigation use a medium-bold weight (650). Fourth-level headings and subfeature names use bold body-sized text. Counts use tabular numerals. Paragraphs and quotations are limited to (75ch), while the objective is limited to (64ch). Raw requirements retain line breaks and use the body font rather than a separate monospace face.

## Layout

The desktop workspace is a centered grid with a maximum width of (1440px), a navigation column of (208px), and a flexible reading column. The header spans the page and has a minimum height of (76px). Navigation is sticky at the top of the viewport. The main reading area uses padding of (40px 48px 28px) and a minimum height of `calc(100vh - 76px)`.

The introduction places the product name and objective opposite the primary download action, separated by (32px). A wrapping toolbar places the scope selector, search field, and live result count together. The search field can grow from (160px) to (340px). Content is presented as a continuous list, with feature rows separated by rules and vertical padding rather than individual card shells.

At a viewport width of (760px) or less:

- The grid becomes a single column. The navigation becomes a wrapping horizontal row, loses its sticky position, and hides its supporting note.
- Header padding becomes (14px 20px), with a minimum height of (64px).
- Main padding becomes (28px 20px). Its desktop minimum-height expression remains unchanged in the current stylesheet.
- The introduction stacks, and the primary action fills the available width with an upper margin of (18px).
- Navigation labels use the label size. The toolbar gap becomes (12px), and the search minimum width becomes (150px).
- Feature metadata moves below its heading. The evidence heading is allowed to wrap.

Long content wraps within the available width, including headings, quotations, list items, and raw requirements. The UI uses no fixed bottom actions or overlay drawers.

Print rules hide the header, navigation, toolbar, all buttons, and footer note; remove main padding; and keep individual disclosure containers together where possible. They do not explicitly open collapsed disclosures or reveal inactive panels. Print is therefore the currently visible review state, not a complete export layout.

## Elevation & Depth

There are no shadows, gradients, blurred surfaces, or lifted cards in the current stylesheet. Depth is expressed through the gray workspace, white reading plane, pale selected region, and thin borders.

**The Flat Surface Rule.** Preserve the distinction between the reading plane and its workspace through tone and rules rather than decorative elevation.

## Shapes

Controls use gently rounded corners; fields use the smaller corner radius in the frontmatter. Reading rows, evidence records, and the reading plane have square edges. Borders are thin (1px), and source references remain rectangular controls rather than pill chips.

The universal sizing model is `border-box`. Buttons, inputs, and selects have a minimum height of (44px). Disclosure summaries have a minimum height of (48px). A keyboard focus outline is (3px) with an offset of (3px).

## Components

### Buttons

Primary download uses blue with white text. Neutral actions, including the contextual return, use white with a divider border. The feature-list export is neutral and separated from the list by an upper margin of (28px).

Button backgrounds transition over (160ms) with `ease-out`. Hover, pressed, and disabled treatments are CSS color states, not movement. The primary action has its own darker hover treatment; its combined hover and pressed appearance follows the existing selector cascade. Disabled buttons use muted text, a gray background, and the default cursor.

### Inputs and filter

The search input and scope select keep native semantics and control behavior. Both use white backgrounds, a stronger field border, and the field corner radius. Labels sit above controls with a gap of (6px). The scope options are all features, MVP, and later versions. Search matches feature names and prioritization reasons immediately.

The result count is a polite live region. A no-match state provides a text instruction to clear search or change the scope. Without a product plan, the filter, search, and backlog download are disabled; the interface shows specific guidance. Inputs have no custom validation-error treatment in this renderer.

### Navigation

Four native buttons switch between scope, planning and metrics, pending decisions, and input evidence. The current panel is identified with `aria-current="page"`, a selected wash, darker blue text, and weight (650). Normal panel changes focus the destination heading. Inactive sections are hidden rather than removed.

A keyboard skip link becomes visible on focus and targets the main reading content. Navigation wraps on mobile instead of becoming a menu.

### Feature rows and metadata

Each feature is an unboxed article with a top rule, name, plain scope and priority text, rationale, associated user problem, and source references. Metadata is a text label without a filled badge, icon, or separate card.

A native disclosure contains subfeatures, user stories, acceptance criteria, and dependencies. Acceptance conditions use repeated given/when/then labels with thin separators. Disclosure state persists across panel switches. Changing the scope filter or search rebuilds the feature list, so its disclosure state resets.

### Source references and evidence records

Source references are compact bordered buttons using blue label text. They retain the standard minimum control height and keyboard focus treatment. Associated assumptions are adjacent supporting text.

Activating a source button stores its origin and the current scroll position, shows the evidence panel, and highlights the matching quotation record. The same contextual return button moves into the selected record above its identifier. The record receives focus and scrolls into view immediately. Evidence includes an identifier, input type and line number, and a quotation preserving its line breaks.

Returning restores the originating panel, focuses the original source button, and restores the saved vertical scroll position. This works from scope, planning, and pending decisions. Because the existing panel DOM is retained, the current filter and disclosure state survive this round trip. The reference highlight remains until another source is selected.

**The Context Return Rule.** A traced quotation keeps its return action beside the quotation, and return preserves the reader's previous place.

### State, motion, and output

The header distinguishes a plan awaiting human review from an input awaiting a product plan. Assumption and constraint counts appear as supporting notice text. Empty planning and decision panels use readable guidance, not loading placeholders.

The highlighted evidence background has a (180ms) `ease-out` transition. Source and return navigation explicitly use instant scrolling. There are no entrance animations. Reduced-motion preference disables transitions and forces automatic scroll behavior.

Downloads are local browser Blob downloads for Markdown and backlog JSON. The renderer embeds its styles, script, and escaped data into one HTML artifact. It does not use a service, network data, or browser persistence. With JavaScript disabled, a text notice points to the Markdown artifact; there is no interactive fallback.

## Do's and Don'ts

### Do:

- **Do** retain gray workspace, white reading surface, blue actions, and thin structural dividers.
- **Do** use plain scope and priority text so meaning remains readable without color.
- **Do** keep source references, exact quotations, and contextual return behavior connected.
- **Do** preserve visible keyboard focus, native controls, and the reduced-motion override.
- **Do** use the implemented wrapping layout and readable text measure when extending this renderer.

### Don't:

- **Don't** turn each feature into a raised or rounded card.
- **Don't** add a middle-dot separator; current labels use a slash, Chinese punctuation, or natural spacing.
- **Don't** add palette tokens or semantic color meanings that the implementation does not establish.
- **Don't** imply that a traceable source or a structural check establishes factual validity or product approval.
- **Don't** treat the sidecar's illustrative tonal ramps or static component previews as additional implemented states.
