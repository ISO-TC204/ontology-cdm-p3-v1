# RailNetwork

A RailNetwork is a type of TransportNetwork using rails on a stabilized base.

![RailNetwork Diagram](../diagrams/RailNetwork.svg)

<a href="../../diagrams/RailNetwork.svg">Open interactive RailNetwork diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [TrackLink](TrackLink.md) |
| partwhole:hasProperPart | only ([RailCorridor](RailCorridor.md) or [RailSection](RailSection.md) or [TrackLink](TrackLink.md)) |
| rdfs:subClassOf | [TransportNetwork](TransportNetwork.md) |

## Other Annotations

- **xsd:pattern**: [RailNetworkPattern](RailNetworkPattern.md)

