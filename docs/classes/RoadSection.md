# RoadSection

A RoadSection is a type of TravelledWaySection that groups RoadLinks and RoadSegments for a useful operational purpose (e.g., assigning a speed limit, designating a traffic control scheme).

![RoadSection Diagram](../diagrams/RoadSection.svg)

<a href="../../diagrams/RoadSection.svg">Open interactive RoadSection diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | only ([RoadLink](RoadLink.md) or [RoadSegment](RoadSegment.md)) |
| partwhole:properPartOf | only [RoadNetwork](RoadNetwork.md) |
| rdfs:subClassOf | [TravelledWaySection](TravelledWaySection.md) |

## Other Annotations

- **xsd:pattern**: [RoadNetworkPattern](RoadNetworkPattern.md)

