# TransportNode

A TransportNode is a NetworkElement that represents a node on the transport network that can be used to designate an end to a link or to join links.

![TransportNode Diagram](../diagrams/TransportNode.svg)

<a href="../../diagrams/TransportNode.svg">Open interactive TransportNode diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| egress | min 1 [TravelledWayLink](TravelledWayLink.md) |
| egress | only [TravelledWayLink](TravelledWayLink.md) |
| ingress | min 1 [TravelledWayLink](TravelledWayLink.md) |
| ingress | only [TravelledWayLink](TravelledWayLink.md) |
| partwhole:properPartOf | min 1 [TransportNetwork](TransportNetwork.md) |
| partwhole:properPartOf | only [TransportNetwork](TransportNetwork.md) |
| rdfs:subClassOf | [NetworkElement](NetworkElement.md) |

## Other Annotations

- **xsd:pattern**: [TransportNetworkPattern](TransportNetworkPattern.md)

