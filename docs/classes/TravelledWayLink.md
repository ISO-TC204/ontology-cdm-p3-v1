# TravelledWayLink

A TravelledWayLink is a type of NetworkElement and transinfras:TravelledWayLink. It represents a contiguous length of a TravelledWay between two TransportNodes of operational or managerial significance.

![TravelledWayLink Diagram](../diagrams/TravelledWayLink.svg)

<a href="../../diagrams/TravelledWayLink.svg">Open interactive TravelledWayLink diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| allowedDirections | max 1 code:Code |
| allowedDirections | only code:Code |
| from | exactly 1 [TransportNode](TransportNode.md) |
| from | only [TransportNode](TransportNode.md) |
| partwhole:hasProperPart | only [TravelledWaySegment](TravelledWaySegment.md) |
| partwhole:properPartOf | min 1 [TransportNetwork](TransportNetwork.md) |
| partwhole:properPartOf | only ([TransportNetwork](TransportNetwork.md) or [TravelledWay](TravelledWay.md) or [TravelledWaySection](TravelledWaySection.md)) |
| rdfs:subClassOf | [NetworkElement](NetworkElement.md) |
| rdfs:subClassOf | transinfras:[TravelledWayLink](TravelledWayLink.md) |
| to | exactly 1 [TransportNode](TransportNode.md) |
| to | only [TransportNode](TransportNode.md) |

## Other Annotations

- **xsd:pattern**: [TransportNetworkPattern](TransportNetworkPattern.md)

