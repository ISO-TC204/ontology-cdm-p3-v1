# RoadLane

A RoadLane is a type of TravelledWayLane that forms part of a RoadSegment.

![RoadLane Diagram](../diagrams/RoadLane.svg)

<a href="../../diagrams/RoadLane.svg">Open interactive RoadLane diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| next | only [RoadLane](RoadLane.md) |
| partwhole:properPartOf | min 1 [RoadSegment](RoadSegment.md) |
| partwhole:properPartOf | only [RoadSegment](RoadSegment.md) |
| previous | only [RoadLane](RoadLane.md) |
| rdfs:subClassOf | [TravelledWayLane](TravelledWayLane.md) |
| width | exactly 1 xsd:nonNegativeInteger |
| width | only xsd:nonNegativeInteger |

## Other Annotations

- **xsd:pattern**: [RoadNetworkPattern](RoadNetworkPattern.md)

