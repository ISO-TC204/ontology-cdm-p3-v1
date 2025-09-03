# Footpath

A Footpath is a type of TravelledWay that is made up of FootpathLinks.

![Footpath Diagram](../diagrams/Footpath.svg)

<a href="../../diagrams/Footpath.svg">Open interactive Footpath diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [FootpathLink](FootpathLink.md) |
| partwhole:hasProperPart | only [FootpathLink](FootpathLink.md) |
| partwhole:properPartOf | only [FootpathNetwork](FootpathNetwork.md) |
| rdfs:subClassOf | [TravelledWay](TravelledWay.md) |

## Other Annotations

- **xsd:pattern**: [PedestrianNetworkPattern](PedestrianNetworkPattern.md)

