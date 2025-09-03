# TrackSegment

A TrackSegment is a type of TravelledWaySegment that represents a portion of a TrackLink with common physical characteristics.

![TrackSegment Diagram](../diagrams/TrackSegment.svg)

<a href="../../diagrams/TrackSegment.svg">Open interactive TrackSegment diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:properPartOf | exactly 1 [TrackLink](TrackLink.md) |
| partwhole:properPartOf | only ([RailSection](RailSection.md) or [TrackLink](TrackLink.md)) |
| rdfs:subClassOf | [TravelledWaySegment](TravelledWaySegment.md) |

## Other Annotations

- **xsd:pattern**: [RailNetworkPattern](RailNetworkPattern.md)

