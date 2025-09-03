# TravelCorridor

A TravelCorridor is a type of TravelledWay that is made up of TravelCorridorLinks.

NOTE: The extent of a TravelCorridor is defined by the extent of the path that shares the designator assigned to the TravelCorridor.

![TravelCorridor Diagram](../diagrams/TravelCorridor.svg)

<a href="../../diagrams/TravelCorridor.svg">Open interactive TravelCorridor diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| partwhole:hasProperPart | min 1 [TravelCorridorLink](TravelCorridorLink.md) |
| partwhole:hasProperPart | only [TravelCorridorLink](TravelCorridorLink.md) |
| rdfs:subClassOf | [TravelledWay](TravelledWay.md) |

## Other Annotations

- **xsd:pattern**: [TravelCorridorPattern](TravelCorridorPattern.md)

