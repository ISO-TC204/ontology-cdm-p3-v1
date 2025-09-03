# Alert

An Alert can be used to notify people of important information.

![Alert Diagram](../diagrams/Alert.svg)

<a href="../../diagrams/Alert.svg">Open interactive Alert diagram</a>

## Formalization

| Property | Value Restriction |
|----------|-------------------|
| activities | only activity:Activity |
| beginTime | max 1 time:Instant |
| beginTime | only time:Instant |
| category | exactly 1 code:Code |
| category | only code:Code |
| cause | only code:Code |
| certainty | max 1 code:Code |
| certainty | only code:Code |
| creationTime | exactly 1 time:Instant |
| creationTime | only time:Instant |
| distribution | exactly 1 code:Code |
| distribution | only code:Code |
| effect | only code:Code |
| endTime | max 1 time:Instant |
| endTime | only time:Instant |
| expiryTime | only time:Instant |
| genProp:hasDescription | exactly 1 xsd:string |
| genProp:hasDescription | only xsd:string |
| headline | exactly 1 xsd:string |
| headline | only xsd:string |
| issuer | exactly 1 xsd:nonNegativeInteger |
| issuer | only xsd:nonNegativeInteger |
| lastUpdateTime | exactly 1 time:Instant |
| lastUpdateTime | only time:Instant |
| location | only geo:Geometry |
| rdfs:subClassOf | [ITSThing](ITSThing.md) |
| recommendation | only code:Code |
| referencedAlert | only [Alert](Alert.md) |
| resources | only xsd:anyURI |
| severity | max 1 code:Code |
| severity | only code:Code |
| status | exactly 1 code:Code |
| status | only code:Code |
| urgency | max 1 code:Code |
| urgency | only code:Code |
| website | only xsd:anyURI |

## Other Annotations

- **xsd:pattern**: [TransportAlertPattern](TransportAlertPattern.md)

