#!/usr/bin/env python3
"""Convert docs/*.owl RDF/XML files to RITSO-style Turtle.

Conventions (aligned with ontology-its-regulation samples):
  - Restrictions are inlined under the class as [ ... ] blank nodes
  - owl:allValuesFrom class fillers become owl:onClass
  - xsd datatype fillers remain owl:allValuesFrom
  - dcterms:description / rdfs:comment are promoted to skos:definition
  - cc:license literals become dcterms:license IRIs
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

NS = Namespace("https://w3id.org/citydata/part3/v1/")
CDM1 = Namespace("https://w3id.org/citydata/part1/v1/")
CDM2 = Namespace("https://w3id.org/citydata/part2/v1/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
VANN = Namespace("http://purl.org/vocab/vann/")
CC = Namespace("http://creativecommons.org/ns#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DASH = Namespace("http://datashapes.org/dash#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
TIME = Namespace("http://www.w3.org/2006/time#")
SCHEMA = Namespace("http://schema.org/")

SUPPRESSED_ANNOTATIONS = {RDFS.comment, DC.description, DCTERMS.description, SKOS.definition, CC.license}

CLASS_ORDER = [
    RDF.type,
    RDFS.subClassOf,
    OWL.equivalentClass,
    OWL.disjointWith,
    OWL.disjointUnionOf,
    DASH.abstract,
    SKOS.definition,
    RDFS.label,
    SKOS.example,
    SKOS.note,
    SKOS.editorialNote,
    RDFS.seeAlso,
]

PROP_ORDER = [
    RDF.type,
    RDFS.subPropertyOf,
    OWL.inverseOf,
    OWL.propertyChainAxiom,
    SKOS.definition,
    RDFS.domain,
    RDFS.range,
    SCHEMA.domainIncludes,
    SCHEMA.rangeIncludes,
    RDFS.label,
]

ONT_ORDER = [
    RDF.type,
    DCTERMS.title,
    SKOS.definition,
    VANN.preferredNamespaceUri,
    VANN.preferredNamespacePrefix,
    CDM1.mainModule,
    DCTERMS.creator,
    DCTERMS.modified,
    OWL.versionInfo,
    OWL.versionIRI,
    DCTERMS.license,
    RDFS.seeAlso,
    DCTERMS.bibliographicCitation,
    OWL.imports,
]

IND_ORDER = [RDF.type, SKOS.definition, RDFS.label]

PREFIX_BINDS = [
    ("", NS),
    ("rdf", RDF),
    ("rdfs", RDFS),
    ("owl", OWL),
    ("xsd", XSD),
    ("skos", SKOS),
    ("dcterms", DCTERMS),
    ("vann", VANN),
    ("dash", DASH),
    ("schema", SCHEMA),
    ("geo", GEO),
    ("time", TIME),
    ("cdm1", CDM1),
    ("cdm2", CDM2),
]


def rewrite_term(term):
    """Normalise known IRI variants so prefixes resolve cleanly."""
    if isinstance(term, URIRef):
        s = str(term)
        if s.startswith("https://www.opengis.net/ont/geosparql#"):
            return URIRef("http://www.opengis.net/ont/geosparql#" + s.split("#", 1)[1])
        if s.startswith("https://www.w3.org/2006/time#"):
            return URIRef("http://www.w3.org/2006/time#" + s.split("#", 1)[1])
        if s.startswith("https://schema.org/"):
            return URIRef("http://schema.org/" + s[len("https://schema.org/") :])
    return term


def load_graph(path: Path) -> Graph:
    g = Graph()
    g.parse(path)
    fixed = Graph()
    for s, p, o in g:
        fixed.add((rewrite_term(s), rewrite_term(p), rewrite_term(o)))
    return fixed


def is_list_node(g: Graph, node) -> bool:
    return isinstance(node, BNode) and ((node, RDF.first, None) in g or node == RDF.nil)


def list_items(g: Graph, node):
    return list(Collection(g, node))


def is_restriction(g: Graph, node) -> bool:
    return isinstance(node, BNode) and (node, RDF.type, OWL.Restriction) in g


def is_class_expr(g: Graph, node) -> bool:
    if not isinstance(node, BNode):
        return False
    if (node, RDF.type, OWL.Class) in g or (node, RDF.type, OWL.Restriction) in g:
        return True
    return any(
        (node, p, None) in g
        for p in (OWL.unionOf, OWL.intersectionOf, OWL.complementOf, OWL.oneOf)
    )


def is_xsd_or_rdf_datatype(term) -> bool:
    if not isinstance(term, URIRef):
        return False
    s = str(term)
    return s.startswith(str(XSD)) or s.startswith(str(RDF))


def restriction_pairs(g: Graph, node: BNode):
    """Predicate/object pairs for a restriction; map class allValuesFrom → onClass."""
    props = {p: o for p, o in g.predicate_objects(node)}
    pairs = [(RDF.type, OWL.Restriction)]

    on_prop = props.get(OWL.onProperty)
    if on_prop is not None:
        pairs.append((OWL.onProperty, on_prop))

    on_class = props.get(OWL.onClass)
    all_from = props.get(OWL.allValuesFrom)
    if on_class is not None:
        pairs.append((OWL.onClass, on_class))
    elif all_from is not None:
        if is_xsd_or_rdf_datatype(all_from):
            pairs.append((OWL.allValuesFrom, all_from))
        else:
            pairs.append((OWL.onClass, all_from))

    for pred in (
        OWL.onDataRange,
        OWL.someValuesFrom,
        OWL.hasValue,
        OWL.cardinality,
        OWL.minCardinality,
        OWL.maxCardinality,
        OWL.qualifiedCardinality,
        OWL.minQualifiedCardinality,
        OWL.maxQualifiedCardinality,
    ):
        if pred in props:
            pairs.append((pred, props[pred]))

    known = {
        RDF.type,
        OWL.onProperty,
        OWL.onClass,
        OWL.allValuesFrom,
        OWL.onDataRange,
        OWL.someValuesFrom,
        OWL.hasValue,
        OWL.cardinality,
        OWL.minCardinality,
        OWL.maxCardinality,
        OWL.qualifiedCardinality,
        OWL.minQualifiedCardinality,
        OWL.maxQualifiedCardinality,
    }
    for pred, obj in sorted(props.items(), key=lambda x: str(x[0])):
        if pred not in known:
            pairs.append((pred, obj))
    return pairs


def definition_text(g: Graph, subject) -> Literal | None:
    for pred in (SKOS.definition, RDFS.comment, DC.description, DCTERMS.description):
        vals = list(g.objects(subject, pred))
        if vals:
            v = vals[0]
            text = str(v).strip()
            # Collapse internal whitespace from multi-line RDF/XML text nodes
            text = " ".join(text.split())
            lang = v.language if isinstance(v, Literal) and v.language else "en"
            return Literal(text, lang=lang)
    return None


def license_iri(g: Graph, subject) -> URIRef | None:
    for pred in (DCTERMS.license, CC.license):
        for obj in g.objects(subject, pred):
            if isinstance(obj, URIRef):
                return obj
            if isinstance(obj, Literal):
                return URIRef(str(obj).strip())
    return None


def qname(term, nsm) -> str:
    if isinstance(term, URIRef):
        s = str(term)
        # Local terms in the default namespace (no further path segments)
        if s.startswith(str(NS)):
            local = s[len(str(NS)) :]
            if local and "/" not in local and "#" not in local:
                return f":{local}"
            # Ontology IRIs like .../Core/ or .../TransportNetworkPattern/
            return f"<{s}>"
        prefix_map = [
            ("cdm1:", str(CDM1)),
            ("cdm2:", str(CDM2)),
            ("schema:", str(SCHEMA)),
            ("geo:", str(GEO)),
            ("time:", str(TIME)),
            ("xsd:", str(XSD)),
            ("owl:", str(OWL)),
            ("rdf:", str(RDF)),
            ("rdfs:", str(RDFS)),
            ("skos:", str(SKOS)),
            ("dcterms:", str(DCTERMS)),
            ("vann:", str(VANN)),
            ("dash:", str(DASH)),
            ("cc:", str(CC)),
        ]
        for pfx, iri in prefix_map:
            if s.startswith(iri):
                local = s[len(iri) :]
                if local and "/" not in local and "#" not in local:
                    return pfx + local
                # Path-style IRIs under cdm1/cdm2 (e.g. .../Core/)
                return f"<{s}>"
        try:
            return term.n3(nsm)
        except Exception:
            return f"<{s}>"
    if isinstance(term, Literal):
        if term.datatype == XSD.boolean:
            return "true" if str(term).lower() in {"true", "1"} else "false"
        return term.n3(nsm)
    if isinstance(term, BNode):
        return "_:" + str(term)
    return str(term)


class TurtleWriter:
    def __init__(self, g: Graph):
        self.g = g
        self.nsm = Graph().namespace_manager
        for pfx, ns in PREFIX_BINDS:
            self.nsm.bind(pfx, ns, override=True)

    def term(self, t) -> str:
        return qname(t, self.nsm)

    def write_collection(self, node, indent: int) -> list[str]:
        items = list_items(self.g, node)
        pad = " " * indent
        if not items:
            return ["()"]
        lines = ["("]
        for item in items:
            rendered = self.write_object(item, indent + 4)
            if len(rendered) == 1:
                lines.append(f"{pad}    {rendered[0]}")
            else:
                lines.append(f"{pad}    {rendered[0]}")
                lines.extend(rendered[1:])
        lines.append(f"{pad})")
        return lines

    def write_bnode(self, node: BNode, indent: int) -> list[str]:
        g = self.g
        pad = " " * indent
        inner = " " * (indent + 4)

        inv = list(g.objects(node, OWL.inverseOf))
        other = [(p, o) for p, o in g.predicate_objects(node) if p != OWL.inverseOf]
        if inv and not other:
            inv_lines = self.write_object(inv[0], indent + 4)
            if len(inv_lines) == 1:
                return [f"[ owl:inverseOf {inv_lines[0]} ]"]
            lines = ["[", f"{inner}owl:inverseOf {inv_lines[0]}"]
            lines.extend(inv_lines[1:])
            lines.append(f"{pad}]")
            return lines

        if is_restriction(g, node):
            pairs = restriction_pairs(g, node)
        elif is_class_expr(g, node):
            pairs = []
            types = list(g.objects(node, RDF.type))
            if OWL.Class in types or not types:
                pairs.append((RDF.type, OWL.Class))
            for pred in (OWL.unionOf, OWL.intersectionOf, OWL.complementOf, OWL.oneOf):
                for obj in g.objects(node, pred):
                    pairs.append((pred, obj))
            for pred, obj in g.predicate_objects(node):
                if pred not in {
                    RDF.type,
                    OWL.unionOf,
                    OWL.intersectionOf,
                    OWL.complementOf,
                    OWL.oneOf,
                }:
                    pairs.append((pred, obj))
        else:
            pairs = sorted(g.predicate_objects(node), key=lambda po: str(po[0]))

        if not pairs:
            return ["[]"]

        lines = ["["]
        for i, (pred, obj) in enumerate(pairs):
            pred_s = self.term(pred)
            obj_lines = self.write_object(obj, indent + 4)
            sep = " ;" if i < len(pairs) - 1 else ""
            pred_col = f"{pred_s:<28} "
            if len(obj_lines) == 1:
                lines.append(f"{inner}{pred_col}{obj_lines[0]}{sep}")
            else:
                lines.append(f"{inner}{pred_col}{obj_lines[0]}")
                for j, ol in enumerate(obj_lines[1:]):
                    if j == len(obj_lines) - 2:
                        lines.append(f"{ol}{sep}")
                    else:
                        lines.append(ol)
        lines.append(f"{pad}]")
        return lines

    def write_object(self, obj, indent: int) -> list[str]:
        if isinstance(obj, BNode):
            if is_list_node(self.g, obj):
                return self.write_collection(obj, indent)
            return self.write_bnode(obj, indent)
        return [self.term(obj)]

    def ordered_po(self, subject, order) -> list[tuple]:
        g = self.g
        used = set()
        result = []

        types = list(g.objects(subject, RDF.type))
        primary = {
            OWL.Class,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
            OWL.NamedIndividual,
            OWL.Ontology,
            OWL.FunctionalProperty,
            OWL.InverseFunctionalProperty,
            OWL.TransitiveProperty,
            OWL.SymmetricProperty,
        }
        types_sorted = sorted(types, key=lambda t: (0 if t in primary else 1, str(t)))
        if types_sorted and order and order[0] == RDF.type:
            for t in types_sorted:
                result.append((RDF.type, t))
            used.add(RDF.type)

        for pred in order:
            if pred == RDF.type:
                continue
            objs = list(g.objects(subject, pred))
            named = sorted([o for o in objs if not isinstance(o, BNode)], key=str)
            blanks = [o for o in objs if isinstance(o, BNode)]
            for o in named + blanks:
                result.append((pred, o))
            if objs:
                used.add(pred)

        remaining = defaultdict(list)
        for pred, obj in g.predicate_objects(subject):
            if pred in used or pred in SUPPRESSED_ANNOTATIONS:
                continue
            remaining[pred].append(obj)
        for pred in sorted(remaining, key=str):
            for obj in remaining[pred]:
                result.append((pred, obj))
        return result

    def write_subject(self, subject, order) -> str:
        g = self.g
        pairs = self.ordered_po(subject, order)

        defn = definition_text(g, subject)
        if defn is not None:
            pairs = [(p, o) for p, o in pairs if p != SKOS.definition]
            insert_at = None
            # Prefer to keep definitions with identity metadata on ontologies
            for i, (p, _) in enumerate(pairs):
                if p == DCTERMS.title:
                    insert_at = i + 1
                    break
            if insert_at is None:
                for i, (p, _) in enumerate(pairs):
                    if p in {
                        RDFS.label,
                        SKOS.example,
                        SKOS.note,
                        SKOS.editorialNote,
                    }:
                        insert_at = i
                        break
            if insert_at is None:
                structural = {
                    RDF.type,
                    RDFS.subClassOf,
                    RDFS.subPropertyOf,
                    OWL.equivalentClass,
                    OWL.disjointWith,
                    OWL.disjointUnionOf,
                    OWL.inverseOf,
                    RDFS.domain,
                    RDFS.range,
                    SCHEMA.domainIncludes,
                    SCHEMA.rangeIncludes,
                    DASH.abstract,
                }
                insert_at = 0
                for i, (p, _) in enumerate(pairs):
                    if p in structural:
                        insert_at = i + 1
            pairs.insert(insert_at, (SKOS.definition, defn))

        lic = license_iri(g, subject)
        if lic is not None:
            pairs = [(p, o) for p, o in pairs if p not in (DCTERMS.license, CC.license)]
            # Place license after creators / before imports when possible
            insert_at = len(pairs)
            for i, (p, _) in enumerate(pairs):
                if p in (OWL.imports, OWL.versionIRI, OWL.versionInfo, DCTERMS.modified):
                    insert_at = i
                    break
            pairs.insert(insert_at, (DCTERMS.license, lic))

        if not pairs:
            return f"{self.term(subject)} .\n"

        formatted = [self.term(subject)]
        for i, (pred, obj) in enumerate(pairs):
            pred_s = self.term(pred)
            obj_lines = self.write_object(obj, 4)
            sep = " ;" if i < len(pairs) - 1 else " ."
            pred_col = f"{pred_s:<28} "
            if len(obj_lines) == 1:
                formatted.append(f"    {pred_col}{obj_lines[0]}{sep}")
            else:
                formatted.append(f"    {pred_col}{obj_lines[0]}")
                for j, ol in enumerate(obj_lines[1:]):
                    if j == len(obj_lines) - 2:
                        formatted.append(f"{ol}{sep}")
                    else:
                        formatted.append(ol)
        return "\n".join(formatted) + "\n"


def prefixes_block() -> str:
    lines = [
        "@prefix : <https://w3id.org/citydata/part3/v1/> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix vann: <http://purl.org/vocab/vann/> .",
        "@prefix dash: <http://datashapes.org/dash#> .",
        "@prefix schema: <http://schema.org/> .",
        "@prefix geo: <http://www.opengis.net/ont/geosparql#> .",
        "@prefix time: <http://www.w3.org/2006/time#> .",
        "@prefix cdm1: <https://w3id.org/citydata/part1/v1/> .",
        "@prefix cdm2: <https://w3id.org/citydata/part2/v1/> .",
    ]
    return "\n".join(lines) + "\n\n"


def section(title: str) -> str:
    bar = "# " + "=" * 48
    return f"\n{bar}\n#                {title}\n{bar}\n\n"


def classify_subjects(g: Graph):
    classes, obj_props, data_props, individuals, ann_props = [], [], [], [], []
    named = sorted(
        {s for s in g.subjects() if isinstance(s, URIRef)},
        key=str,
    )
    for s in named:
        types = set(g.objects(s, RDF.type))
        if OWL.Ontology in types:
            continue
        if OWL.AnnotationProperty in types:
            # Skip built-in / external annotation property declarations
            if str(s).startswith(str(NS)):
                ann_props.append(s)
            continue
        if OWL.ObjectProperty in types:
            obj_props.append(s)
        elif OWL.DatatypeProperty in types:
            data_props.append(s)
        elif OWL.Class in types:
            classes.append(s)
        elif OWL.NamedIndividual in types or (
            types
            and OWL.Class not in types
            and OWL.ObjectProperty not in types
            and OWL.DatatypeProperty not in types
        ):
            individuals.append(s)
    return classes, obj_props, data_props, individuals, ann_props


def convert_file(owl_path: Path) -> Path:
    g = load_graph(owl_path)
    writer = TurtleWriter(g)

    parts = [prefixes_block()]

    ontologies = sorted(g.subjects(RDF.type, OWL.Ontology), key=str)
    for ont in ontologies:
        parts.append(writer.write_subject(ont, ONT_ORDER))
        parts.append("\n")

    classes, obj_props, data_props, individuals, ann_props = classify_subjects(g)

    if obj_props:
        parts.append(section("Object Properties"))
        for s in obj_props:
            parts.append(writer.write_subject(s, PROP_ORDER))
            parts.append("\n")

    if data_props:
        parts.append(section("Data Properties"))
        for s in data_props:
            parts.append(writer.write_subject(s, PROP_ORDER))
            parts.append("\n")

    if classes:
        parts.append(section("Classes"))
        for s in classes:
            parts.append(writer.write_subject(s, CLASS_ORDER))
            parts.append("\n")

    if individuals:
        parts.append(section("Individuals"))
        for s in individuals:
            parts.append(writer.write_subject(s, IND_ORDER))
            parts.append("\n")

    if ann_props:
        parts.append(section("Annotation Properties"))
        for s in ann_props:
            parts.append(writer.write_subject(s, [RDF.type, SKOS.definition, RDFS.label]))
            parts.append("\n")

    ttl_path = owl_path.with_suffix(".ttl")
    text = "".join(parts).rstrip() + "\n"
    ttl_path.write_text(text, encoding="utf-8")
    return ttl_path


def main():
    owl_files = sorted(DOCS.glob("*.owl"))
    # Prefer CorePattern.owl over legacy Core.owl when both exist
    names = {p.name for p in owl_files}
    if "CorePattern.owl" in names and "Core.owl" in names:
        owl_files = [p for p in owl_files if p.name != "Core.owl"]
    if not owl_files:
        raise SystemExit(f"No *.owl files found in {DOCS}")

    print(f"Converting {len(owl_files)} OWL file(s) in {DOCS}")
    for owl_path in owl_files:
        ttl_path = convert_file(owl_path)
        print(f"  {owl_path.name} -> {ttl_path.name} ({ttl_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
