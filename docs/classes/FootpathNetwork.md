# FootpathNetwork

A FootpathNetwork is a type of TransportNetwork designed for the use of pedestrians but may be used by others as well.

![FootpathNetwork Diagram](../diagrams/FootpathNetwork.svg)

<a href="../../diagrams/FootpathNetwork.svg">Open interactive FootpathNetwork diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [FootpathLink](FootpathLink.md) |
| partwhole:hasProperPart | only ([Footpath](Footpath.md) or [FootpathLink](FootpathLink.md) or [FootpathSection](FootpathSection.md)) |
| rdfs:subClassOf | [TransportNetwork](TransportNetwork.md) |

## Other Annotations

- **xsd:pattern**: [PedestrianNetworkPattern](PedestrianNetworkPattern.md)

