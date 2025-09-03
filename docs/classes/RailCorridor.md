# RailCorridor

A RailCorridor is a type of TravelledWay that is made up of TrackLinks.

![RailCorridor Diagram](../diagrams/RailCorridor.svg)

<a href="../../diagrams/RailCorridor.svg">Open interactive RailCorridor diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [TrackLink](TrackLink.md) |
| partwhole:hasProperPart | only [TrackLink](TrackLink.md) |
| partwhole:properPartOf | only [RailNetwork](RailNetwork.md) |
| rdfs:subClassOf | [TravelledWay](TravelledWay.md) |

## Other Annotations

- **xsd:pattern**: [RailNetworkPattern](RailNetworkPattern.md)

