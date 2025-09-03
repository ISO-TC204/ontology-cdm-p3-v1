# PublicTransportLine

A PublicTransportLine is one or more routes used by public transport vehicles to transport passengers to and from designated locations.

![PublicTransportLine Diagram](../diagrams/PublicTransportLine.svg)

<a href="../../diagrams/PublicTransportLine.svg">Open interactive PublicTransportLine diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| allowedDirections | min 1 code:Code |
| allowedDirections | only code:Code |
| partwhole:hasProperPart | min 1 [PublicTransportRoute](PublicTransportRoute.md) |
| partwhole:hasProperPart | only [PublicTransportRoute](PublicTransportRoute.md) |
| partwhole:properPartOf | only ([GroupOfLines](GroupOfLines.md) or [PublicTransportSystem](PublicTransportSystem.md)) |
| rdfs:subClassOf | [PublicTransportElement](PublicTransportElement.md) |

## Other Annotations

- **xsd:pattern**: [PublicTransportSystemPattern](PublicTransportSystemPattern.md)

