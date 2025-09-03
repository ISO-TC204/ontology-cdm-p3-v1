# GroupOfLines

A GroupOfLines is a logical grouping of PublicTransportLines for any useful purpose.

![GroupOfLines Diagram](../diagrams/GroupOfLines.svg)

<a href="../../diagrams/GroupOfLines.svg">Open interactive GroupOfLines diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [PublicTransportLine](PublicTransportLine.md) |
| partwhole:hasProperPart | only [PublicTransportLine](PublicTransportLine.md) |
| partwhole:properPartOf | only [PublicTransportSystem](PublicTransportSystem.md) |
| rdfs:subClassOf | [PublicTransportElement](PublicTransportElement.md) |

## Other Annotations

- **xsd:pattern**: [PublicTransportSystemPattern](PublicTransportSystemPattern.md)

