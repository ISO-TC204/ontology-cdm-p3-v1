# PointOnRoute

A PointOnRoute represents an ordered RoutePoint for a PublicTransportRoute.

![PointOnRoute Diagram](../diagrams/PointOnRoute.svg)

<a href="../../diagrams/PointOnRoute.svg">Open interactive PointOnRoute diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| index | exactly 1 xsd:integer |
| index | only xsd:integer |
| point | exactly 1 [RoutePoint](RoutePoint.md) |
| point | only [RoutePoint](RoutePoint.md) |
| rdfs:subClassOf | [PublicTransportElement](PublicTransportElement.md) |
| routePointType | only code:Code |

## Other Annotations

- **xsd:pattern**: [PublicTransportSystemPattern](PublicTransportSystemPattern.md)

