![Draft for review only](/assets/img/draft_for_review.svg)

# PointOnRoute

A PointOnRoute represents an ordered RoutePoint for a PublicTransportRoute.

![PointOnRoute Diagram](diagrams/PointOnRoute.dot.svg)

<a href="diagrams/PointOnRoute.dot.svg">Open interactive PointOnRoute diagram</a>

## Formalization for PointOnRoute

| Property | Constraint |
|----------|------------|
| index | exactly 1 owl:Thing |
| routePoint | exactly 1 owl:Thing |
| routePointType | all cdm2:Code |
| subClassOf | PublicTransportElement |

