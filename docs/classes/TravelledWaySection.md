# TravelledWaySection

A TravelledWaySection is a type of NetworkElement that represents an aggregation of TravelledWayLinks and TravelledWaySegments that jointly represent a contiguous length of a path that shares the same management and operational strategies (within the scope of interest of the implementation).

![TravelledWaySection Diagram](../diagrams/TravelledWaySection.svg)

<a href="../../diagrams/TravelledWaySection.svg">Open interactive TravelledWaySection diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | only ([TravelledWayLink](TravelledWayLink.md) or [TravelledWaySegment](TravelledWaySegment.md)) |
| partwhole:properPartOf | min 1 [TransportNetwork](TransportNetwork.md) |
| partwhole:properPartOf | only [TransportNetwork](TransportNetwork.md) |
| rdfs:subClassOf | [NetworkElement](NetworkElement.md) |

## Other Annotations

- **xsd:pattern**: [TransportNetworkPattern](TransportNetworkPattern.md)

