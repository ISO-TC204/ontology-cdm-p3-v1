![Draft for review only](/assets/img/draft_for_review.svg)

# RoutePoint

A RoutePoint represents a point of interest along a PublicTransportRoute.

![RoutePoint Diagram](diagrams/RoutePoint.dot.svg)

<a href="diagrams/RoutePoint.dot.svg">Open interactive RoutePoint diagram</a>

## Formalization for RoutePoint

| Property | Constraint |
|----------|------------|
| isBorderCrossing | exactly 1 owl:Thing |
| isViaPoint | max 1 owl:Thing |
| subClassOf | PublicTransportElement |
| subClassOf | TransportNode |

