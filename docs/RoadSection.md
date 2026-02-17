![Draft for review only](/assets/img/draft_for_review.svg)

# RoadSection

A RoadSection is a type of TravelledWaySection that groups RoadLinks and RoadSegments for a useful operational purpose (e.g., assigning a speed limit, designating a traffic control scheme).

![RoadSection Diagram](diagrams/RoadSection.dot.svg)

<a href="diagrams/RoadSection.dot.svg">Open interactive RoadSection diagram</a>

## Specializations of RoadSection

| Class | Description |
|-------|-------------|
| [Micromobility Path Section](MicromobilityPathSection.md) | A MicromobilityPathSections is a type of RoadSection that groups MicromobilityLinks and MicromobilityPathSegments for a useful operational purpose (e.g., assigning a speed limit, designating areas of shared use). |

## Formalization for RoadSection

| Property | Constraint |
|----------|------------|
| cdm1:hasProperPart | all RoadLink or RoadSegment |
| cdm1:properPartOf | all RoadNetwork |
| subClassOf | TravelledWaySection |

