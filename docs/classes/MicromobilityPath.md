# MicromobilityPath

A MicromobilityPath is a type of Road that is made up of MicromobilityPathLinks.

![MicromobilityPath Diagram](../diagrams/MicromobilityPath.svg)

<a href="../../diagrams/MicromobilityPath.svg">Open interactive MicromobilityPath diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [MicromobilityLink](MicromobilityLink.md) |
| partwhole:hasProperPart | only [MicromobilityLink](MicromobilityLink.md) |
| partwhole:properPartOf | only [MicromobilityNetwork](MicromobilityNetwork.md) |
| rdfs:subClassOf | [Road](Road.md) |

## Other Annotations

- **xsd:pattern**: [MicromobilityNetworkPattern](MicromobilityNetworkPattern.md)

