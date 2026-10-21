# LaTeX float layout diagnosis

The apparent paragraph cut around Figure 6 and Table 1 is caused by LaTeX
float placement, not by missing or overlapping text.

Both objects use the `figure` or `table` float environments with the
`[htbp]` placement specifier. These letters are placement preferences rather
than strict instructions. Because there was not enough suitable space at the
insertion points, LaTeX deferred Figure 6 and Table 1. It continued composing
the following prose on PDF page 29, then placed the pending floats on page 30
before printing the last two lines of the paragraph that begins with
"A Figura 7 mostra...".

The compilation log contains no relevant overfull-box, oversized-float, or
overlap warning for this passage. The output is therefore valid according to
the page builder, although its reading order is visually undesirable.

Possible controls, from least to most restrictive, are:

- Add float barriers at section boundaries with the `placeins` package, for
  example `\usepackage[section]{placeins}`.
- Insert `\FloatBarrier` at a deliberate boundary where every pending float
  must be printed before later prose.
- Use `[H]` from the `float` package only when an object must remain exactly at
  its source position. This is rigid and may leave excessive white space.
- Reorder or resize the objects so that LaTeX can place them naturally.

Using `[!htbp]` can relax some internal placement limits, but it still does not
guarantee source-order placement. `\clearpage` also flushes floats, but is a
strong page-breaking command and is usually unnecessary for this case.
