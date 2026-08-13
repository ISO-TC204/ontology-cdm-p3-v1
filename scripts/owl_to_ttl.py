#!/usr/bin/env python3
"""Convert CDM Part 3 OWL/XML modules to Protege/OWLAPI-style Turtle.

Pattern files keep OWL class definitions with *inline* restriction blank nodes.
Validation companions are emitted as *SHACL.ttl.

Layout matches Protege's Turtle export (section banners, ``### IRI`` markers,
aligned predicates, full IRIs for ontology subjects) so diffs against Protege
saves are useful.

Usage:
  python scripts/owl_to_ttl.py              # convert from *.owl (if present)
  python scripts/owl_to_ttl.py --reformat   # re-serialize existing docs/*.ttl
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD, DCTERMS

from protege_turtle import serialize_protege

DOCS = Path(__file__).resolve().parents[1] / "docs"
NS = Namespace("https://w3id.org/citydata/part3/v1/")
CDM1 = Namespace("https://w3id.org/citydata/part1/v1/")
CDM2 = Namespace("https://w3id.org/citydata/part2/v1/")
CC = Namespace("http://creativecommons.org/ns#")
VANN = Namespace("http://purl.org/vocab/vann/")
SH = Namespace("http://www.w3.org/ns/shacl#")
TIME = Namespace("http://www.w3.org/2006/time#")
PROV = Namespace("http://www.w3.org/ns/prov#")
ORG = Namespace("http://www.w3.org/ns/org#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
I72 = Namespace("https://w3id.org/citydata/21972/v1/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DASH = Namespace("http://datashapes.org/dash#")
SCHEMA = Namespace("http://schema.org/")

# Known incorrect https spellings in some OWL sources → canonical http IRIs
IRI_REWRITE: dict[str, str] = {
    "https://www.w3.org/2006/time#": "http://www.w3.org/2006/time#",
    "https://www.opengis.net/ont/geosparql#": "http://www.opengis.net/ont/geosparql#",
}

# Source OWL filename -> (pattern ttl, shacl ttl, ontology local name matching pattern file stem)
MODULES: dict[str, tuple[str, str, str]] = {
    "Core.owl": ("CorePattern.ttl", "CoreSHACL.ttl", "CorePattern"),
    "CorePattern.owl": ("CorePattern.ttl", "CoreSHACL.ttl", "CorePattern"),
    "MicromobilityNetworkPattern.owl": (
        "MicromobilityNetworkPattern.ttl",
        "MicromobilityNetworkSHACL.ttl",
        "MicromobilityNetworkPattern",
    ),
    "PedestrianNetworkPattern.owl": (
        "PedestrianNetworkPattern.ttl",
        "PedestrianNetworkSHACL.ttl",
        "PedestrianNetworkPattern",
    ),
    "PublicTransportSystemPattern.owl": (
        "PublicTransportSystemPattern.ttl",
        "PublicTransportSystemSHACL.ttl",
        "PublicTransportSystemPattern",
    ),
    "RailNetworkPattern.owl": (
        "RailNetworkPattern.ttl",
        "RailNetworkSHACL.ttl",
        "RailNetworkPattern",
    ),
    "RoadNetworkPattern.owl": (
        "RoadNetworkPattern.ttl",
        "RoadNetworkSHACL.ttl",
        "RoadNetworkPattern",
    ),
    "TransportAlertPattern.owl": (
        "TransportAlertPattern.ttl",
        "TransportAlertSHACL.ttl",
        "TransportAlertPattern",
    ),
    "TransportNetworkPattern.owl": (
        "TransportNetworkPattern.ttl",
        "TransportNetworkSHACL.ttl",
        "TransportNetworkPattern",
    ),
    "TravelCorridorPattern.owl": (
        "TravelCorridorPattern.ttl",
        "TravelCorridorSHACL.ttl",
        "TravelCorridorPattern",
    ),
}

PREFIX_MAP: list[tuple[str, str]] = [
    ("", str(NS)),
    ("cdm3", str(NS)),  # explicit preferred prefix (RITSO / ont2md)
    ("cdm1", str(CDM1)),
    ("cdm2", str(CDM2)),
    ("cc", str(CC)),
    ("dash", str(DASH)),
    ("dcterms", str(DCTERMS)),
    ("owl", str(OWL)),
    ("rdf", str(RDF)),
    ("rdfs", str(RDFS)),
    ("sh", str(SH)),
    ("skos", str(SKOS)),
    ("vann", str(VANN)),
    ("xsd", str(XSD)),
    ("time", str(TIME)),
    ("prov", str(PROV)),
    ("org", str(ORG)),
    ("geo", str(GEO)),
    ("i72", str(I72)),
    ("foaf", str(FOAF)),
    ("schema", str(SCHEMA)),
]

# Only always declare the default namespace. Other prefixes are added when their
# IRIs appear in the graph (owl:imports, cdm1:/cdm2: terms, etc.).
ALWAYS_DECLARE_PREFIXES = frozenset({""})



def ontology_iri(local: str) -> URIRef:
    """Ontology document IRI with no trailing slash (for ont2md module names)."""
    return URIRef(f"{NS}{local}")


def shacl_local_name(pattern_local: str) -> str:
    """Map CityPattern -> CitySHACL, CorePattern -> CoreSHACL (matches *.ttl stem)."""
    if pattern_local.endswith("Pattern"):
        return pattern_local[: -len("Pattern")] + "SHACL"
    return pattern_local + "SHACL"


def shacl_iri(pattern_local: str) -> URIRef:
    """SHACL ontology IRI matches the SHACL filename stem, e.g. :CitySHACL."""
    return ontology_iri(shacl_local_name(pattern_local))


def rewrite_uri(term):
    """Normalize known incorrect https namespace spellings."""
    if not isinstance(term, URIRef):
        return term
    s = str(term)
    for bad, good in IRI_REWRITE.items():
        if s.startswith(bad):
            return URIRef(good + s[len(bad) :])
    return term


def strip_module_slash(uri: URIRef) -> URIRef:
    """Drop trailing slash on module ontology IRIs (…/CityPattern/ → …/CityPattern).

    Leaves the namespace root and version IRIs (…/Module/r3.0/) unchanged.
    """
    s = str(uri)
    for base in (str(NS), str(CDM1), str(CDM2)):
        if s == base:
            return uri
        if s.startswith(base) and s.endswith("/"):
            rest = s[len(base) : -1]
            if rest and "/" not in rest:
                return URIRef(base + rest)
    return uri


def rename_module_iri(uri: URIRef) -> URIRef:
    """Align ontology document IRIs with TTL filenames (Core -> CorePattern)."""
    s = str(uri)
    for base in (str(NS), str(CDM1), str(CDM2)):
        if s == f"{base}Core":
            return URIRef(f"{base}CorePattern")
        old_ver = f"{base}Core/"
        if s.startswith(old_ver):
            return URIRef(f"{base}CorePattern/" + s[len(old_ver) :])
    return uri


def normalize_graph_iris(g: Graph) -> None:
    """Rewrite terms in-place: https→http fixes and module IRI slash stripping."""
    triples = list(g)
    g.remove((None, None, None))
    for s, p, o in triples:
        ns, np, no = rewrite_uri(s), rewrite_uri(p), rewrite_uri(o)
        if isinstance(ns, URIRef):
            ns = rename_module_iri(strip_module_slash(ns))
        if isinstance(no, URIRef):
            no = rename_module_iri(strip_module_slash(no))
        if isinstance(np, URIRef):
            np = rename_module_iri(strip_module_slash(np))
        g.add((ns, np, no))


def _pn_local_ok(local: str) -> bool:
    """Turtle PN_LOCAL is restrictive; reject paths and empty fragments."""
    if local == "":
        return True  # bare prefix like time:
    # Allow simple names: letters, digits, _, -, .
    import re

    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_\-\.]*", local) is not None


def qname(term, prefixes: dict[str, str]) -> str:
    if isinstance(term, Literal):
        # Boolean literals without quotes
        if term.datatype == XSD.boolean:
            return "true" if str(term).lower() == "true" else "false"
        text = (
            str(term)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\r\n", "\\n")
            .replace("\n", "\\n")
            .replace("\r", "\\n")
            .replace("\t", "\\t")
        )
        if term.datatype:
            return f'"{text}"^^{qname(term.datatype, prefixes)}'
        if term.language:
            return f'"{text}"@{term.language}'
        return f'"{text}"'
    if isinstance(term, BNode):
        return f"_:{term}"
    s = str(term)
    # Longest prefix match
    best = None
    for pfx, uri in prefixes.items():
        if s.startswith(uri):
            if best is None or len(uri) > len(best[1]):
                best = (pfx, uri)
    if best:
        pfx, uri = best
        local = s[len(uri) :]
        if _pn_local_ok(local):
            if pfx == "":
                return f":{local}" if local else ":"
            return f"{pfx}:{local}" if local else f"{pfx}:"
    return f"<{s}>"


def is_restriction(g: Graph, node) -> bool:
    return (node, RDF.type, OWL.Restriction) in g


def is_class_expr(g: Graph, node) -> bool:
    if isinstance(node, URIRef):
        return True
    if not isinstance(node, BNode):
        return False
    return (
        is_restriction(g, node)
        or (node, OWL.intersectionOf, None) in g
        or (node, OWL.unionOf, None) in g
        or (node, OWL.oneOf, None) in g
        or (node, OWL.complementOf, None) in g
        or (node, RDF.type, OWL.Class) in g
    )


def list_items(g: Graph, head) -> list:
    try:
        return list(Collection(g, head))
    except Exception:
        items = []
        cur = head
        while cur and cur != RDF.nil:
            first = g.value(cur, RDF.first)
            if first is not None:
                items.append(first)
            cur = g.value(cur, RDF.rest)
        return items


def transform_restriction(g: Graph, node: BNode) -> None:
    """Rewrite OWL restriction vocabulary toward RITSO / Protege style.

    - owl:someValuesFrom C -> owl:onClass C + owl:minQualifiedCardinality 1
    - owl:allValuesFrom C stays as allValuesFrom unless a cardinality is present,
      in which case it becomes owl:onClass C (qualified restriction form)
    - unqualified onClass / onDataRange (no cardinality) -> owl:allValuesFrom
    - onDataRange with a non-XSD filler is corrected to onClass
    """
    has_card = any(
        g.value(node, p) is not None
        for p in (
            OWL.qualifiedCardinality,
            OWL.minQualifiedCardinality,
            OWL.maxQualifiedCardinality,
            OWL.cardinality,
            OWL.minCardinality,
            OWL.maxCardinality,
        )
    )

    # Mis-tagged: onDataRange must be a datatype
    on_data = g.value(node, OWL.onDataRange)
    if on_data is not None and not str(on_data).startswith(str(XSD)):
        g.remove((node, OWL.onDataRange, on_data))
        if g.value(node, OWL.onClass) is None:
            g.add((node, OWL.onClass, on_data))

    avf = g.value(node, OWL.allValuesFrom)
    if avf is not None and has_card:
        # Qualified cardinality restrictions use onClass / onDataRange
        g.remove((node, OWL.allValuesFrom, avf))
        if (node, OWL.onClass, None) not in g and (node, OWL.onDataRange, None) not in g:
            if str(avf).startswith(str(XSD)):
                g.add((node, OWL.onDataRange, avf))
            else:
                g.add((node, OWL.onClass, avf))

    svf = g.value(node, OWL.someValuesFrom)
    if svf is not None:
        g.remove((node, OWL.someValuesFrom, svf))
        if (node, OWL.onClass, None) not in g and (node, OWL.onDataRange, None) not in g:
            if str(svf).startswith(str(XSD)):
                g.add((node, OWL.onDataRange, svf))
            else:
                g.add((node, OWL.onClass, svf))
        if (
            (node, OWL.minQualifiedCardinality, None) not in g
            and (node, OWL.qualifiedCardinality, None) not in g
            and (node, OWL.minCardinality, None) not in g
        ):
            g.add(
                (
                    node,
                    OWL.minQualifiedCardinality,
                    Literal(1, datatype=XSD.nonNegativeInteger),
                )
            )

    # Unqualified onClass / onDataRange (no cardinality) is invalid OWL; use allValuesFrom
    has_card_now = any(
        g.value(node, p) is not None
        for p in (
            OWL.qualifiedCardinality,
            OWL.minQualifiedCardinality,
            OWL.maxQualifiedCardinality,
            OWL.cardinality,
            OWL.minCardinality,
            OWL.maxCardinality,
        )
    )
    if not has_card_now and g.value(node, OWL.allValuesFrom) is None:
        on_class = g.value(node, OWL.onClass)
        if on_class is not None:
            g.remove((node, OWL.onClass, on_class))
            g.add((node, OWL.allValuesFrom, on_class))
        on_data = g.value(node, OWL.onDataRange)
        if on_data is not None:
            g.remove((node, OWL.onDataRange, on_data))
            g.add((node, OWL.allValuesFrom, on_data))

    # Qualified cardinality without onClass/onDataRange is invalid; demote to unqualified
    if g.value(node, OWL.onClass) is None and g.value(node, OWL.onDataRange) is None:
        swaps = (
            (OWL.qualifiedCardinality, OWL.cardinality),
            (OWL.minQualifiedCardinality, OWL.minCardinality),
            (OWL.maxQualifiedCardinality, OWL.maxCardinality),
        )
        for qpred, upred in swaps:
            val = g.value(node, qpred)
            if val is not None:
                g.remove((node, qpred, val))
                if g.value(node, upred) is None:
                    g.add((node, upred, val))


def transform_graph(g: Graph) -> None:
    for restr in list(g.subjects(RDF.type, OWL.Restriction)):
        if isinstance(restr, BNode):
            transform_restriction(g, restr)


def collect_reachable_bnodes(g: Graph, root, seen: set | None = None) -> set:
    if seen is None:
        seen = set()
    if not isinstance(root, BNode) or root in seen:
        return seen
    seen.add(root)
    for _, _, o in g.triples((root, None, None)):
        collect_reachable_bnodes(g, o, seen)
    return seen


def write_property_expr(g: Graph, node, prefixes: dict[str, str], indent: str) -> list[str]:
    """Serialize a property expression (URI or inverse blank node)."""
    if isinstance(node, URIRef):
        return [f"{indent}{qname(node, prefixes)}"]
    inv = g.value(node, OWL.inverseOf)
    if inv is not None:
        return [f"{indent}[ owl:inverseOf {qname(inv, prefixes)} ]"]
    return [f"{indent}{qname(node, prefixes)}"]


def write_restriction(g: Graph, node, prefixes: dict[str, str], indent: str) -> list[str]:
    lines = [f"{indent}["]
    inner = indent + "    "
    props = [
        (RDF.type, "rdf:type"),
        (OWL.onProperty, "owl:onProperty"),
        (OWL.onClass, "owl:onClass"),
        (OWL.onDataRange, "owl:onDataRange"),
        (OWL.qualifiedCardinality, "owl:qualifiedCardinality"),
        (OWL.minQualifiedCardinality, "owl:minQualifiedCardinality"),
        (OWL.maxQualifiedCardinality, "owl:maxQualifiedCardinality"),
        (OWL.cardinality, "owl:cardinality"),
        (OWL.minCardinality, "owl:minCardinality"),
        (OWL.maxCardinality, "owl:maxCardinality"),
        (OWL.hasValue, "owl:hasValue"),
        (OWL.allValuesFrom, "owl:allValuesFrom"),
        (OWL.someValuesFrom, "owl:someValuesFrom"),
        (OWL.complementOf, "owl:complementOf"),
    ]
    entries: list[list[str]] = []
    for pred, label in props:
        for obj in g.objects(node, pred):
            if pred == OWL.onProperty and isinstance(obj, BNode):
                expr = write_property_expr(g, obj, prefixes, inner + "    ")
                first = expr[0].strip()
                entries.append([f"{inner}{label:<28} {first} ;"])
            elif isinstance(obj, BNode) and is_class_expr(g, obj):
                expr = write_class_expr(g, obj, prefixes, inner + "    ")
                first = expr[0].strip()
                block = [f"{inner}{label:<28} {first}"]
                block.extend(expr[1:])
                entries.append(block)
            else:
                entries.append([f"{inner}{label:<28} {qname(obj, prefixes)} ;"])
    flat: list[str] = []
    for i, block in enumerate(entries):
        is_last = i == len(entries) - 1
        for j, line in enumerate(block):
            if j == len(block) - 1:
                line = line.rstrip(" ;")
                if not is_last:
                    line = line + " ;"
            flat.append(line)
    lines.extend(flat)
    lines.append(f"{indent}]")
    return lines


def write_class_expr(g: Graph, node, prefixes: dict[str, str], indent: str) -> list[str]:
    if isinstance(node, URIRef) or isinstance(node, Literal):
        return [f"{indent}{qname(node, prefixes)}"]
    if is_restriction(g, node):
        return write_restriction(g, node, prefixes, indent)

    # complementOf alone
    comp = g.value(node, OWL.complementOf)
    if comp is not None and (node, OWL.intersectionOf, None) not in g and (
        node,
        OWL.unionOf,
        None,
    ) not in g:
        lines = [f"{indent}["]
        inner = indent + "    "
        if (node, RDF.type, OWL.Class) in g:
            lines.append(f"{inner}rdf:type owl:Class ;")
        if isinstance(comp, BNode) and is_class_expr(g, comp):
            expr = write_class_expr(g, comp, prefixes, inner + "    ")
            lines.append(f"{inner}owl:complementOf {expr[0].strip()}")
            lines.extend(expr[1:])
        else:
            lines.append(f"{inner}owl:complementOf {qname(comp, prefixes)}")
        lines.append(f"{indent}]")
        return lines

    for pred, label in (
        (OWL.intersectionOf, "owl:intersectionOf"),
        (OWL.unionOf, "owl:unionOf"),
        (OWL.oneOf, "owl:oneOf"),
    ):
        head = g.value(node, pred)
        if head is not None:
            items = list_items(g, head)
            lines = [f"{indent}["]
            inner = indent + "    "
            lines.append(f"{inner}rdf:type owl:Class ;")
            lines.append(f"{inner}{label} (")
            for item in items:
                item_lines = write_class_expr(g, item, prefixes, inner + "    ")
                if len(item_lines) == 1:
                    lines.append(f"{inner}    {item_lines[0].strip()}")
                else:
                    # keep nested expression indented
                    first = item_lines[0].strip()
                    lines.append(f"{inner}    {first}")
                    lines.extend(item_lines[1:])
            lines.append(f"{inner})")
            lines.append(f"{indent}]")
            return lines

    # Fallback blank node dump
    lines = [f"{indent}["]
    for p, o in g.predicate_objects(node):
        if isinstance(o, BNode) and is_class_expr(g, o):
            expr = write_class_expr(g, o, prefixes, indent + "        ")
            lines.append(f"{indent}    {qname(p, prefixes)} {expr[0].strip()}")
            lines.extend(expr[1:])
            lines[-1] = lines[-1] + " ;"
        else:
            lines.append(f"{indent}    {qname(p, prefixes)} {qname(o, prefixes)} ;")
    if len(lines) > 1 and lines[-1].endswith(" ;"):
        lines[-1] = lines[-1][:-2]
    lines.append(f"{indent}]")
    return lines


def write_rdf_list(g: Graph, head, prefixes: dict[str, str], indent: str) -> list[str]:
    items = list_items(g, head)
    if not items:
        return [f"{indent}()"]
    lines = [f"{indent}("]
    for item in items:
        # Property chain members may be blank nodes with owl:inverseOf
        if isinstance(item, BNode) and (item, OWL.inverseOf, None) in g:
            inv = g.value(item, OWL.inverseOf)
            lines.append(f"{indent}    [ owl:inverseOf {qname(inv, prefixes)} ]")
        else:
            expr = write_class_expr(g, item, prefixes, indent + "    ")
            if len(expr) == 1:
                lines.append(f"{indent}    {expr[0].strip()}")
            else:
                lines.extend(expr)
    lines.append(f"{indent})")
    return lines


ANNOTATION_ORDER = [
    DCTERMS.title,
    DCTERMS.alternative,
    SKOS.definition,
    VANN.preferredNamespaceUri,
    VANN.preferredNamespacePrefix,
    CDM1.mainModule,
    DCTERMS.creator,
    DCTERMS.bibliographicCitation,
    RDFS.seeAlso,
    RDFS.comment,
    OWL.priorVersion,
    DCTERMS.modified,
    OWL.versionInfo,
    OWL.versionIRI,
    CC.license,
    OWL.imports,
]

PROP_ORDER = [
    RDF.type,
    RDFS.subPropertyOf,
    OWL.inverseOf,
    SKOS.definition,
    SKOS.note,
    SKOS.closeMatch,
    RDFS.domain,
    RDFS.range,
    RDFS.comment,
    OWL.propertyChainAxiom,
]

CLASS_ORDER = [
    RDF.type,
    SKOS.definition,
    RDFS.subClassOf,
    OWL.disjointWith,
    OWL.equivalentClass,
    OWL.oneOf,
    RDFS.comment,
]

INDIVIDUAL_ORDER = [
    RDF.type,
    RDFS.label,
    SKOS.definition,
    RDFS.comment,
]


def ordered_predicates(preds: Iterable, order: list) -> list:
    preds = list(set(preds))
    ranked = []
    for i, p in enumerate(order):
        if p in preds:
            ranked.append(p)
            preds.remove(p)
    ranked.extend(sorted(preds, key=str))
    return ranked


def subject_sort_key(s, g: Graph):
    types = set(g.objects(s, RDF.type))
    if OWL.Ontology in types:
        return (0, str(s))
    if OWL.AnnotationProperty in types:
        return (1, str(s))
    if OWL.ObjectProperty in types or OWL.DatatypeProperty in types:
        return (2, str(s))
    if OWL.Class in types:
        return (3, str(s))
    if OWL.NamedIndividual in types:
        return (4, str(s))
    return (5, str(s))


def write_subject(g: Graph, subject, prefixes: dict[str, str], consumed: set) -> str:
    types = set(g.objects(subject, RDF.type))
    if OWL.Ontology in types:
        order = ANNOTATION_ORDER + [RDF.type]
    elif OWL.Class in types:
        order = CLASS_ORDER
    elif OWL.ObjectProperty in types or OWL.DatatypeProperty in types:
        order = PROP_ORDER
    elif OWL.NamedIndividual in types:
        order = INDIVIDUAL_ORDER
    else:
        order = [RDF.type, SKOS.definition, RDFS.subClassOf, RDFS.subPropertyOf]

    preds = ordered_predicates([p for p, _ in g.predicate_objects(subject)], order)
    lines = [f"{qname(subject, prefixes)}"]
    pred_blocks = []
    for pred in preds:
        objs = list(g.objects(subject, pred))
        # Stable sort URIRefs first
        objs.sort(key=lambda o: (0 if isinstance(o, URIRef) else 1, str(o)))
        for obj in objs:
            if isinstance(obj, BNode) and obj in consumed:
                continue
            if pred in (RDFS.subClassOf, OWL.equivalentClass, OWL.disjointWith) and is_class_expr(
                g, obj
            ):
                if isinstance(obj, BNode):
                    consumed.update(collect_reachable_bnodes(g, obj))
                expr_lines = write_class_expr(g, obj, prefixes, "    ")
                if len(expr_lines) == 1 and not expr_lines[0].strip().startswith("["):
                    pred_blocks.append(
                        [f"    {qname(pred, prefixes):<24} {expr_lines[0].strip()} ;"]
                    )
                else:
                    # Put '[' on the same line as the predicate (RITSO style)
                    first = expr_lines[0].strip()
                    block = [f"    {qname(pred, prefixes)} {first}"]
                    for el in expr_lines[1:]:
                        block.append(el)
                    block[-1] = block[-1] + " ;"
                    pred_blocks.append(block)
            elif pred == OWL.propertyChainAxiom and isinstance(obj, BNode):
                consumed.update(collect_reachable_bnodes(g, obj))
                # propertyChainAxiom may point directly at rdf:List head
                list_lines = write_rdf_list(g, obj, prefixes, "        ")
                block = [f"    {qname(pred, prefixes)}"]
                block.extend(list_lines)
                block[-1] = block[-1] + " ;"
                pred_blocks.append(block)
            elif pred in (OWL.intersectionOf, OWL.unionOf, OWL.oneOf) and isinstance(obj, BNode):
                consumed.update(collect_reachable_bnodes(g, obj))
                list_lines = write_rdf_list(g, obj, prefixes, "        ")
                block = [f"    {qname(pred, prefixes)}"]
                block.extend(list_lines)
                block[-1] = block[-1] + " ;"
                pred_blocks.append(block)
            else:
                if isinstance(obj, BNode):
                    # Skip blank nodes that are only restriction/list internals
                    if is_restriction(g, obj) or (obj, RDF.first, None) in g:
                        consumed.update(collect_reachable_bnodes(g, obj))
                        continue
                    consumed.update(collect_reachable_bnodes(g, obj))
                    expr_lines = write_class_expr(g, obj, prefixes, "    ")
                    first = expr_lines[0].strip()
                    block = [f"    {qname(pred, prefixes)} {first}"]
                    for el in expr_lines[1:]:
                        block.append(el)
                    block[-1] = block[-1] + " ;"
                    pred_blocks.append(block)
                else:
                    pred_blocks.append(
                        [f"    {qname(pred, prefixes):<24} {qname(obj, prefixes)} ;"]
                    )

    flat = []
    for block in pred_blocks:
        flat.extend(block)
    if flat:
        flat[-1] = flat[-1].rstrip(" ;") + " ."
    lines.extend(flat)
    return "\n".join(lines)


def used_prefixes(g: Graph) -> dict[str, str]:
    needed = {p: u for p, u in PREFIX_MAP if p in ALWAYS_DECLARE_PREFIXES}
    text_terms = []
    for s, p, o in g:
        text_terms.extend([s, p, o])
        if isinstance(o, Literal) and o.datatype:
            text_terms.append(o.datatype)
    for term in text_terms:
        if not isinstance(term, URIRef):
            continue
        s = str(term)
        # Prefer longest namespace match, skipping empty/default and cdm3 aliases
        # when a more specific external prefix applies.
        matches = [(pfx, uri) for pfx, uri in PREFIX_MAP if s.startswith(uri)]
        if matches:
            matches.sort(key=lambda x: len(x[1]), reverse=True)
            for pfx, uri in matches:
                if pfx in ("", "cdm3") and any(len(u) > len(uri) for _, u in matches):
                    continue
                needed[pfx] = uri
                break
    return needed


def serialize_pattern(g: Graph) -> str:
    """Serialize an OWL module graph as Protege/OWLAPI-style Turtle."""
    normalize_graph_iris(g)
    transform_graph(g)
    # Normalize mainModule string literals to boolean (property lives in cdm1)
    for s, o in list(g.subject_objects(CDM1.mainModule)):
        if isinstance(o, Literal) and str(o).lower() in ("true", "false"):
            g.remove((s, CDM1.mainModule, o))
            g.add((s, CDM1.mainModule, Literal(str(o).lower() == "true")))
    prefixes = used_prefixes(g)
    ordered = {p: u for p, u in PREFIX_MAP if p in prefixes}
    ordered.update({p: u for p, u in prefixes.items() if p not in ordered})
    return serialize_protege(g, ordered, str(NS))


def restriction_to_shacl_props(g: Graph, class_uri: URIRef) -> list[dict]:
    props = []
    for obj in g.objects(class_uri, RDFS.subClassOf):
        if not is_restriction(g, obj):
            continue
        path = g.value(obj, OWL.onProperty)
        if path is None:
            continue
        entry: dict = {}
        if isinstance(path, BNode):
            inv = g.value(path, OWL.inverseOf)
            if inv is None:
                continue
            entry["inversePath"] = inv
        else:
            entry["path"] = path

        on_class = g.value(obj, OWL.onClass)
        on_data = g.value(obj, OWL.onDataRange)
        avf = g.value(obj, OWL.allValuesFrom)
        # Skip complex class expressions in SHACL (anonymous intersections/unions)
        if on_class is not None:
            if isinstance(on_class, BNode):
                continue
            entry["class"] = on_class
        elif avf is not None and not str(avf).startswith(str(XSD)):
            if isinstance(avf, BNode):
                continue
            entry["class"] = avf
        if on_data is not None:
            if isinstance(on_data, BNode):
                continue
            entry["datatype"] = on_data
        elif avf is not None and str(avf).startswith(str(XSD)):
            entry["datatype"] = avf

        qc = g.value(obj, OWL.qualifiedCardinality)
        minq = g.value(obj, OWL.minQualifiedCardinality)
        maxq = g.value(obj, OWL.maxQualifiedCardinality)
        minc = g.value(obj, OWL.minCardinality)
        maxc = g.value(obj, OWL.maxCardinality)
        card = g.value(obj, OWL.cardinality)

        if qc is not None:
            n = int(qc)
            if n == 1:
                entry["node"] = "ExactlyOneShape"
            elif n == 0:
                entry["maxCount"] = 0
            else:
                entry["minCount"] = n
                entry["maxCount"] = n
        elif minq is not None:
            n = int(minq)
            if n == 1 and maxq is None:
                entry["node"] = "MinOneShape"
            else:
                entry["minCount"] = n
                if maxq is not None:
                    entry["maxCount"] = int(maxq)
        elif maxq is not None:
            n = int(maxq)
            if n == 1:
                entry["node"] = "MaxOneShape"
            else:
                entry["maxCount"] = n
        elif card is not None:
            n = int(card)
            if n == 1:
                entry["node"] = "ExactlyOneShape"
            else:
                entry["minCount"] = n
                entry["maxCount"] = n
        elif minc is not None:
            entry["minCount"] = int(minc)
            if maxc is not None:
                entry["maxCount"] = int(maxc)
        elif maxc is not None:
            if int(maxc) == 1:
                entry["node"] = "MaxOneShape"
            else:
                entry["maxCount"] = int(maxc)
        props.append(entry)
    return props


def write_shacl(pattern_g: Graph, local: str, label: str) -> str:
    """Build SHACL companion from class restrictions in the (pre-transform) graph."""
    g = Graph()
    for t in pattern_g:
        g.add(t)
    normalize_graph_iris(g)
    transform_graph(g)

    shapes = []
    for cls in sorted(g.subjects(RDF.type, OWL.Class), key=str):
        if not isinstance(cls, URIRef):
            continue
        props = restriction_to_shacl_props(g, cls)
        if not props:
            continue
        shapes.append((cls, props))

    prefixes = {p: u for p, u in PREFIX_MAP}

    # Collect URIRefs used so we can emit needed prefixes
    used_uris: set[str] = set()
    for cls, props in shapes:
        used_uris.add(str(cls))
        for p in props:
            if "path" in p:
                used_uris.add(str(p["path"]))
            if "inversePath" in p:
                used_uris.add(str(p["inversePath"]))
            if "class" in p:
                used_uris.add(str(p["class"]))
            if "datatype" in p:
                used_uris.add(str(p["datatype"]))

    needed_pfx = set(ALWAYS_DECLARE_PREFIXES)
    for uri in used_uris:
        for pfx, base in PREFIX_MAP:
            if uri.startswith(base):
                needed_pfx.add(pfx)
                break

    lines = []
    for pfx, uri in PREFIX_MAP:
        if pfx in needed_pfx:
            if pfx == "":
                lines.append(f"@prefix : <{uri}> .")
            else:
                lines.append(f"@prefix {pfx}: <{uri}> .")
    lines.append("")

    shacl_id = shacl_local_name(local)
    lines.append(f":{shacl_id}")
    lines.append("    rdf:type owl:Ontology ;")
    lines.append(f'    dcterms:title "City Data Model Part 2 - {label} - SHACL constraints" ;')
    lines.append(
        f'    skos:definition "SHACL validation shapes for the {label} module." ;'
    )
    lines.append(f'    vann:preferredNamespaceUri "{NS}" ;')
    lines.append('    vann:preferredNamespacePrefix "cdm2" ;')
    if local != "CorePattern":
        lines.append(f"    owl:imports :{local} ;")
        lines.append("    owl:imports :CoreSHACL .")
    else:
        lines.append("    owl:imports :CorePattern .")
    lines.append("")

    if local == "CorePattern":
        lines.extend(
            [
                ":ExactlyOneShape",
                "    rdf:type sh:NodeShape ;",
                "    sh:minCount 1 ;",
                "    sh:maxCount 1 .",
                "",
                ":MinOneShape",
                "    rdf:type sh:NodeShape ;",
                "    sh:minCount 1 .",
                "",
                ":MaxOneShape",
                "    rdf:type sh:NodeShape ;",
                "    sh:maxCount 1 .",
                "",
            ]
        )

    for cls, props in shapes:
        local_name = str(cls)[len(str(NS)) :]
        if not _pn_local_ok(local_name):
            continue
        shape = f":{local_name}Shape"
        lines.append(f"{shape}")
        lines.append("    rdf:type sh:NodeShape ;")
        lines.append(f"    sh:targetClass {qname(cls, prefixes)} ;")
        for i, p in enumerate(props):
            lines.append("    sh:property [")
            if "inversePath" in p:
                lines.append(
                    f"        sh:path [ sh:inversePath {qname(p['inversePath'], prefixes)} ] ;"
                )
            else:
                lines.append(f"        sh:path {qname(p['path'], prefixes)} ;")
            if "node" in p:
                lines.append(f"        sh:node :{p['node']} ;")
            if "minCount" in p:
                lines.append(f"        sh:minCount {p['minCount']} ;")
            if "maxCount" in p:
                lines.append(f"        sh:maxCount {p['maxCount']} ;")
            if "class" in p:
                lines.append(f"        sh:class {qname(p['class'], prefixes)} ;")
            if "datatype" in p:
                lines.append(f"        sh:datatype {qname(p['datatype'], prefixes)} ;")
            if lines[-1].endswith(" ;"):
                lines[-1] = lines[-1][:-2]
            closing = "    ] ;" if i < len(props) - 1 else "    ] ."
            lines.append(closing)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def convert_module(owl_name: str, pattern_name: str, shacl_name: str, local: str) -> None:
    owl_path = DOCS / owl_name
    g = Graph()
    g.parse(owl_path, format="xml")

    label = "".join((" " + c if c.isupper() else c) for c in local).strip()
    shacl_text = write_shacl(g, local, label)

    pattern_text = serialize_pattern(g)
    (DOCS / pattern_name).write_text(pattern_text, encoding="utf-8")
    (DOCS / shacl_name).write_text(shacl_text, encoding="utf-8")
    print(f"Wrote {pattern_name}, {shacl_name}")


def write_master() -> None:
    g = Graph()
    g.parse(DOCS / "5087-3.owl", format="xml")
    normalize_graph_iris(g)
    # Add SHACL imports into the graph before serialization
    master = URIRef(str(NS))
    for _, _, local in MODULES.values():
        g.add((master, OWL.imports, shacl_iri(local)))
    # Normalize mainModule to boolean
    for o in list(g.objects(master, CDM1.mainModule)):
        g.remove((master, CDM1.mainModule, o))
    g.add((master, CDM1.mainModule, Literal(True)))
    text = serialize_pattern(g)
    (DOCS / "5087-3.ttl").write_text(text, encoding="utf-8")
    print("Wrote 5087-3.ttl")


def write_catalog() -> None:
    """Write Protege catalog: module IRIs plus every named entity → defining file.

    Protege often tries to dereference class/property IRIs when they appear
    undeclared; mapping each entity to its defining TTL avoids web fetches.
    """
    from rdflib import Graph as _Graph

    def collect_entities(docs_dir: Path, ns: str, uri_prefix: str) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for path in sorted(docs_dir.glob("*.ttl")):
            g = _Graph()
            g.parse(path)
            rel = f"{uri_prefix}/{path.name}" if uri_prefix != "." else path.name
            for s in g.subjects():
                if not isinstance(s, URIRef):
                    continue
                s_str = str(s)
                if not s_str.startswith(ns):
                    continue
                local = s_str[len(ns) :]
                if not local or "/" in local:
                    continue
                mapping.setdefault(s_str, rel)
        return mapping

    def module_entries(docs_dir: Path, ns: str, uri_prefix: str, master: str):
        entries = [(ns, f"{uri_prefix}/{master}" if uri_prefix != "." else master)]
        for path in sorted(docs_dir.glob("*Pattern.ttl")) + sorted(docs_dir.glob("*SHACL.ttl")):
            g = _Graph()
            g.parse(path)
            ontos = [s for s in g.subjects(RDF.type, OWL.Ontology) if isinstance(s, URIRef)]
            iri = str(ontos[0]).rstrip("/") if ontos else f"{ns}{path.stem}"
            rel = f"{uri_prefix}/{path.name}" if uri_prefix != "." else path.name
            entries.append((iri, rel))
        return entries

    p3_docs = DOCS
    p2_docs = DOCS.parents[1] / "ontology-cdm-p2" / "docs"
    p1_docs = DOCS.parents[1] / "ontology-cdm-p1" / "docs"
    i72_docs = DOCS.parents[1] / "ontology-i72-v1" / "docs"
    geo = "../../ontology-import-geo/docs/geo.ttl"

    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<catalog prefer="public" xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">',
        '    <group prefer="public">',
    ]
    seen: set[str] = set()

    def emit(section: str, modules, entities=None):
        lines.append(f"        <!-- {section} -->")
        for name, uri in modules:
            if name in seen:
                continue
            seen.add(name)
            lines.append(f'        <uri name="{name}" uri="{uri}"/>')
        if entities:
            lines.append(f"        <!-- {section} entities -->")
            for name in sorted(entities):
                if name in seen:
                    continue
                seen.add(name)
                lines.append(f'        <uri name="{name}" uri="{entities[name]}"/>')

    emit(
        "Part 3 modules (this repository)",
        module_entries(p3_docs, str(NS), ".", "5087-3.ttl"),
        collect_entities(p3_docs, str(NS), "."),
    )
    if p2_docs.is_dir():
        emit(
            "Part 2 modules",
            module_entries(p2_docs, str(CDM2), "../../ontology-cdm-p2/docs", "5087-2.ttl"),
            collect_entities(p2_docs, str(CDM2), "../../ontology-cdm-p2/docs"),
        )
    if p1_docs.is_dir():
        emit(
            "Part 1 modules",
            module_entries(p1_docs, str(CDM1), "../../ontology-cdm-p1/docs", "5087-1.ttl"),
            collect_entities(p1_docs, str(CDM1), "../../ontology-cdm-p1/docs"),
        )
    i72_ns = "https://w3id.org/citydata/21972/v1/"
    i72_modules = [
        (i72_ns, "../../ontology-i72-v1/docs/i72.ttl"),
        (i72_ns.rstrip("/"), "../../ontology-i72-v1/docs/i72.ttl"),
        ("http://www.opengis.net/ont/geosparql#", geo),
    ]
    i72_entities = collect_entities(i72_docs, i72_ns, "../../ontology-i72-v1/docs") if i72_docs.is_dir() else {}
    emit("ISO 21972 / GeoSPARQL", i72_modules, i72_entities)

    lines.extend(["    </group>", "</catalog>", ""])
    (DOCS / "catalog-v001.xml").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote catalog-v001.xml ({len(seen)} uri entries)")



def reformat_existing_ttl() -> None:
    """Re-serialize existing pattern/master TTL files in Protege layout (no OWL sources)."""
    paths = sorted(DOCS.glob("*Pattern.ttl")) + [DOCS / "5087-3.ttl"]
    for path in paths:
        if not path.is_file():
            continue
        g = Graph()
        g.parse(path, format="turtle")
        text = serialize_pattern(g)
        # Round-trip check
        g2 = Graph()
        g2.parse(data=text, format="turtle")
        if len(g2) < len(g) * 0.9:
            raise SystemExit(
                f"{path.name}: reformatted graph shrank suspiciously ({len(g)} → {len(g2)})"
            )
        path.write_text(text, encoding="utf-8")
        print(f"Reformatted {path.name} ({len(g)} → {len(g2)} triples)")


def reformat_existing_shacl() -> None:
    """Re-serialize existing *SHACL.ttl files in Protege layout."""
    for path in sorted(DOCS.glob("*SHACL.ttl")):
        g = Graph()
        g.parse(path, format="turtle")
        # Normalize import IRIs (strip trailing slash, Core→CorePattern, https→http)
        normalize_graph_iris(g)
        prefixes = used_prefixes(g)
        ordered = {p: u for p, u in PREFIX_MAP if p in prefixes}
        ordered.update({p: u for p, u in prefixes.items() if p not in ordered})
        text = serialize_protege(g, ordered, str(NS))
        g2 = Graph()
        g2.parse(data=text, format="turtle")
        path.write_text(text, encoding="utf-8")
        print(f"Reformatted {path.name} ({len(g)} → {len(g2)} triples)")


def main() -> int:
    import sys

    if "--reformat" in sys.argv or "-r" in sys.argv:
        reformat_existing_ttl()
        reformat_existing_shacl()
        return 0

    for owl_name, (pattern, shacl, local) in MODULES.items():
        convert_module(owl_name, pattern, shacl, local)
    write_master()
    write_catalog()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
