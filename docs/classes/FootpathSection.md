# FootpathSection

A FootpathSection is a type of TravelledWaySection that groups FootpathLinks and FootpathSegments for a useful operational purpose.

![FootpathSection Diagram](../diagrams/FootpathSection.svg)

<a href="../../diagrams/FootpathSection.svg">Open interactive FootpathSection diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | only ([FootpathLink](FootpathLink.md) or [FootpathSegment](FootpathSegment.md)) |
| partwhole:properPartOf | only [FootpathNetwork](FootpathNetwork.md) |
| rdfs:subClassOf | [TravelledWaySection](TravelledWaySection.md) |

## Other Annotations

- **xsd:pattern**: [PedestrianNetworkPattern](PedestrianNetworkPattern.md)

