# RoadLink

A RoadLink is a type of TravelledWayLink and transinfras:RoadLink using a stabilized base designed for the movement of vehicles that conform to a specified set of requirements but may be used by others as well.

![RoadLink Diagram](../diagrams/RoadLink.svg)

<a href="../../diagrams/RoadLink.svg">Open interactive RoadLink diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| capacity | exactly 1 xsd:nonNegativeInteger |
| capacity | only xsd:nonNegativeInteger |
| maxLanes | exactly 1 xsd:nonNegativeInteger |
| maxLanes | only xsd:nonNegativeInteger |
| partwhole:hasProperPart | only [RoadSegment](RoadSegment.md) |
| partwhole:properPartOf | only ([Road](Road.md) or [RoadNetwork](RoadNetwork.md) or [RoadSection](RoadSection.md)) |
| primaryUser | only [RoadLinkUserType](RoadLinkUserType.md) |
| rdfs:subClassOf | [TravelledWayLink](TravelledWayLink.md) |
| rdfs:subClassOf | transinfras:[RoadLink](RoadLink.md) |
| travelTime | max 1 cityunits:Duration |
| travelTime | only cityunits:Duration |
| usedBy | only [RoadLinkUserType](RoadLinkUserType.md) |

## Other Annotations

- **xsd:pattern**: [RoadNetworkPattern](RoadNetworkPattern.md)

