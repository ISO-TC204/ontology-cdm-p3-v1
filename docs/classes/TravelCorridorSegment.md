# TravelCorridorSegment

A TravelCorridorSegment is a type of TravelledWaySegment that logically groups multiple TravelledWaySegments together as being co-located or side-by-side.

![TravelCorridorSegment Diagram](../diagrams/TravelCorridorSegment.svg)

<a href="../../diagrams/TravelCorridorSegment.svg">Open interactive TravelCorridorSegment diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| corridorElement | min 1 [TravelledWaySegment](TravelledWaySegment.md) |
| corridorElement | only [TravelledWaySegment](TravelledWaySegment.md) |
| partwhole:properPartOf | only [TravelCorridorLink](TravelCorridorLink.md) |
| rdfs:subClassOf | [TravelledWaySegment](TravelledWaySegment.md) |

## Other Annotations

- **xsd:pattern**: [TravelCorridorPattern](TravelCorridorPattern.md)

