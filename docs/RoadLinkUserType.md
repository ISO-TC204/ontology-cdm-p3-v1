![Draft for review only](/assets/img/draft_for_review.svg)

# RoadLinkUserType

A RoadLinkUserType represents the unique combination of a RoadLink and a UserType such that speed limits and other characteristics can be defined to apply to specific user types when operating along a particular road link.

![RoadLinkUserType Diagram](diagrams/RoadLinkUserType.dot.svg)

<a href="diagrams/RoadLinkUserType.dot.svg">Open interactive RoadLinkUserType diagram</a>

## Formalization for RoadLinkUserType

| Property | Constraint |
|----------|------------|
| speedLimit | max 1 owl:Thing |
| subClassOf | ITSThing |
| travelTime | max 1 owl:Thing |
| userCategory | exactly 1 owl:Thing |
| uses | all RoadLink |

## Used by classes

| Class | Property |
|-------|----------|
| [Road Link](RoadLink.md) | primaryUser |
| [Road Link](RoadLink.md) | usedBy |

