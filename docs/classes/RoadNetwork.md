# RoadNetwork

A RoadNetwork is a type of TransportNetwork using a stabilized base designed for the movement of vehicles, other than rail or air vehicles, that conform to a specified set of requirements but may be used by others as well.

![RoadNetwork Diagram](../diagrams/RoadNetwork.svg)

<a href="../../diagrams/RoadNetwork.svg">Open interactive RoadNetwork diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [RoadLink](RoadLink.md) |
| partwhole:hasProperPart | only ([Road](Road.md) or [RoadLink](RoadLink.md) or [RoadSection](RoadSection.md)) |
| rdfs:subClassOf | [TransportNetwork](TransportNetwork.md) |

## Other Annotations

- **xsd:pattern**: [RoadNetworkPattern](RoadNetworkPattern.md)

