# ATP to ATPDraw Project Conversion Research

Research date: 2026-08-27

## Objective

Find GitHub projects that convert an ATP simulation input deck (`.atp`)
into an ATPDraw project in XML or binary ACP format.

## Finding

No public GitHub project was found that performs a general conversion from
an arbitrary `.atp` input deck to an editable ATPDraw XML or `.acp` project.

This is not a symmetric format conversion. ATPDraw is a graphical
preprocessor that generates the ATP input deck. Its project contains data
that the generated `.atp` file does not preserve, including component
positions, icons, captions, local component definitions, and other editor
metadata. A reverse converter therefore needs to infer a schematic layout
and map ATP cards back to ATPDraw components. Some constructs may not have a
unique reverse mapping.

ATPDraw 7 supports two relevant project representations:

- `.acp`: the standard compressed/binary project representation.
- XML: an exchange representation introduced in ATPDraw 7 and described by
  its documentation as less complete than ACP.

## Relevant GitHub projects

### LineCableModels.jl

Repository: <https://github.com/Electa-Git/LineCableModels.jl>

The Julia package contains an ATPDraw XML exporter at
`src/importexport/atp.jl`. It creates an ATPDraw-compatible project with one
LCC component from the package's own line/cable domain model. It is the best
public reference found for generating ATPDraw XML, but it does not parse or
convert arbitrary `.atp` decks.

### LineCableLab

Repository: <https://github.com/amaurigmartins/LineCableLab>

The MATLAB function
`line_export_funs/exportCrossSection2XML.m` writes ATPDraw XML for an LCC
line/cable cross-section. It is useful as another concrete XML-generation
reference, but it does not accept an `.atp` input deck.

### LCCRipper

Repository: <https://github.com/amaurigmartins/LCCRipper>

This MATLAB application reads an ATPDraw XML project and splits an existing
LCC object into multiple sections. Its README explicitly requires XML rather
than the standard binary ACP file. It is an XML consumer/editor, not an ATP
deck converter.

### lccmultiplier

Repository: <https://github.com/lusabar/lccmultiplier>

This Julia CLI reads an ATPDraw XML project and replicates an LCC component.
It is useful for understanding and modifying ATPDraw XML, but it requires a
project already exported by ATPDraw.

### pyATP

Repository: <https://github.com/pdb5627/pyATP>

This Python project includes ATP-related parsing utilities, particularly for
line-constant output. It does not generate ATPDraw XML or ACP, but parts of
its parsing approach could be reused in a limited converter.

### atp-cases-generator

Repository: <https://github.com/munizrodrigo/atp-cases-generator>

This Python project models ATP cards and generates ATP cases. Its direction
is toward `.atp`, not ATPDraw projects. It may still provide reusable card
models for an ATP parser.

## Practical conclusion

For a known and limited subset of ATP cards, a new converter can be built by
combining:

1. an ATP card parser;
2. a mapping from supported cards to ATPDraw XML components;
3. deterministic automatic schematic placement;
4. warnings or fallback objects for unsupported cards;
5. validation by opening the XML in ATPDraw and regenerating the `.atp`
   deck for semantic comparison.

Generating XML is preferable to writing `.acp` directly because the XML
format is designed for exchange and has public examples. ATPDraw can then
open the XML and save the project as `.acp`.

## Primary references

- ATPDraw home: <https://www.atpdraw.net/index.php>
- ATPDraw project format documentation:
  <https://www.atpdraw.net/help7/html_atpdraw_components.html>
- ATPDraw file menu documentation:
  <https://www.atpdraw.net/help/file_menu.htm>
