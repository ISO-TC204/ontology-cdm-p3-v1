![Draft for review only](/assets/img/draft_for_review.svg)

# RoadNetwork

A RoadNetwork is a type of TransportNetwork using a stabilized base designed for the movement of vehicles, other than rail or air vehicles, that conform to a specified set of requirements but may be used by others as well.

![RoadNetwork Diagram](diagrams/RoadNetwork.dot.svg)

<a href="diagrams/RoadNetwork.dot.svg">Open interactive RoadNetwork diagram</a>

## Specializations of RoadNetwork

| Class | Description |
|-------|-------------|
| [Micromobility Network](MicromobilityNetwork.md) | A MicromobilityNetwork is a type of RoadNetwork designed for the use of micromobility vehicles, which have more limited performance characteristics than motor vehicles. |

## Formalization for RoadNetwork

| Property | Constraint |
|----------|------------|
| cdm1:hasProperPart | all Road or RoadLink or RoadSection |
| cdm1:hasProperPart | min 1 owl:Thing |
| subClassOf | TransportNetwork |

## Used by classes

| Class | Property |
|-------|----------|
| [Road](Road.md) | cdm1:properPartOf |
| [Road Section](RoadSection.md) | cdm1:properPartOf |

