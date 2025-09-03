# RoadSegment

A RoadSegment is a type of TravelledWaySegment and transinfas:RoadSegment that represents a portion of a RoadLink with common physical characteristics.

![RoadSegment Diagram](../diagrams/RoadSegment.svg)

<a href="../../diagrams/RoadSegment.svg">Open interactive RoadSegment diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| numLanes | exactly 1 xsd:nonNegativeInteger |
| numLanes | only xsd:nonNegativeInteger |
| partwhole:hasProperPart | min 1 [RoadLane](RoadLane.md) |
| partwhole:hasProperPart | only [RoadLane](RoadLane.md) |
| partwhole:properPartOf | exactly 1 [RoadLink](RoadLink.md) |
| partwhole:properPartOf | only ([RoadLink](RoadLink.md) or [RoadSection](RoadSection.md)) |
| pavementType | max 1 code:Code |
| pavementType | only code:Code |
| rdfs:subClassOf | [TravelledWaySegment](TravelledWaySegment.md) |
| rdfs:subClassOf | transinfras:[RoadSegment](RoadSegment.md) |
| width | exactly 1 xsd:nonNegativeInteger |
| width | only xsd:nonNegativeInteger |

## Other Annotations

- **xsd:pattern**: [RoadNetworkPattern](RoadNetworkPattern.md)

