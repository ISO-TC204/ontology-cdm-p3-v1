![Draft for review only](/assets/img/draft_for_review.svg)

# PublicTransportElement

![PublicTransportElement Diagram](diagrams/PublicTransportElement.dot.svg)

<a href="diagrams/PublicTransportElement.dot.svg">Open interactive PublicTransportElement diagram</a>

## Specializations of PublicTransportElement

| Class | Description |
|-------|-------------|
| [Group Of Lines](GroupOfLines.md) | A GroupOfLines is a logical grouping of PublicTransportLines for any useful purpose. |
| [Point On Route](PointOnRoute.md) | A PointOnRoute represents an ordered RoutePoint for a PublicTransportRoute. |
| [Public Transport Line](PublicTransportLine.md) | A PublicTransportLine is one or more routes used by public transport vehicles to transport passengers to and from designated locations. |
| [Public Transport Route](PublicTransportRoute.md) | A PublicTransportRoute represents one specific path used by a public transport vehicle to transport passengers to and from designated locations. |
| [Public Transport System](PublicTransportSystem.md) | A PublicTransportSystem provides transport services to members of the public. |
| [Route Point](RoutePoint.md) | A RoutePoint represents a point of interest along a PublicTransportRoute. |

## Formalization for PublicTransportElement

| Property | Constraint |
|----------|------------|
| subClassOf | PublicTransportSystemThing |
| subClassOf | cdm2:InfrastructureElement |

