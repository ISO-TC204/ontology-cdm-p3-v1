# MicromobilityPathSegment

A MicromobilityPathSegment is a type of RoadSegment that represents a portion of a MicromobilityLink with common physical characteristics.

![MicromobilityPathSegment Diagram](../diagrams/MicromobilityPathSegment.svg)

<a href="../../diagrams/MicromobilityPathSegment.svg">Open interactive MicromobilityPathSegment diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [MicromobilityLane](MicromobilityLane.md) |
| partwhole:hasProperPart | only [MicromobilityLane](MicromobilityLane.md) |
| partwhole:properPartOf | min 1 [MicromobilityLink](MicromobilityLink.md) |
| partwhole:properPartOf | only ([MicromobilityLink](MicromobilityLink.md) or [MicromobilityPathSection](MicromobilityPathSection.md)) |
| rdfs:subClassOf | [RoadSegment](RoadSegment.md) |

## Other Annotations

- **xsd:pattern**: [MicromobilityNetworkPattern](MicromobilityNetworkPattern.md)

