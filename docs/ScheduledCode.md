![Draft for review only](/assets/img/draft_for_review.svg)

# ScheduledCode

The operational status of an entity, e.g., open or closed.

![ScheduledCode Diagram](diagrams/ScheduledCode.dot.svg)

<a href="diagrams/ScheduledCode.dot.svg">Open interactive ScheduledCode diagram</a>

## Formalization for ScheduledCode

| Property | Constraint |
|----------|------------|
| subClassOf | ITSThing |
| subClassOf | cdm2:Code |
| timeInterval | all time1:DateTimeInterval |
| timeInterval | exactly 1 owl:Thing |

## Used by classes

| Class | Property |
|-------|----------|
| [Network Element](NetworkElement.md) | status |

## Other annotations

| Property | Value |
|----------|-------|
| xsd:pattern | TransportNetworkPattern |

