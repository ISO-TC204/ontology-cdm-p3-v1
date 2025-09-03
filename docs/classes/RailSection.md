# RailSection

A RailSection is a type of TravelledWaySection that groups TrackLinks and TrackSegments for a useful operational purpose (e.g., assigning a speed limit, designating a traffic control scheme).

![RailSection Diagram](../diagrams/RailSection.svg)

<a href="../../diagrams/RailSection.svg">Open interactive RailSection diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | only ([TrackLink](TrackLink.md) or [TrackSegment](TrackSegment.md)) |
| partwhole:properPartOf | only [RailNetwork](RailNetwork.md) |
| rdfs:subClassOf | [TravelledWaySection](TravelledWaySection.md) |

## Other Annotations

- **xsd:pattern**: [RailNetworkPattern](RailNetworkPattern.md)

