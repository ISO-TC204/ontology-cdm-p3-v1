# TravelledWayLane

A TravelledWayLane is a NetworkElement that is a portion of TravelledWaySegment intended to accommodate a single line of moving material entities (e.g., vehicles) along its length.

![TravelledWayLane Diagram](../diagrams/TravelledWayLane.svg)

<a href="../../diagrams/TravelledWayLane.svg">Open interactive TravelledWayLane diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:properPartOf | min 1 [TravelledWaySegment](TravelledWaySegment.md) |
| partwhole:properPartOf | only [TravelledWaySegment](TravelledWaySegment.md) |
| rdfs:subClassOf | [NetworkElement](NetworkElement.md) |

## Other Annotations

- **xsd:pattern**: [TransportNetworkPattern](TransportNetworkPattern.md)

