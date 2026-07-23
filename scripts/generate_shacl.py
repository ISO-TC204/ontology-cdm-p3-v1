#!/usr/bin/env python3
"""Generate RITSO/CDM-style SHACL files from docs/*Pattern.ttl.

Produces:
  docs/CoreSHACL.ttl
  docs/<Name>SHACL.ttl  for each <Name>Pattern.ttl that defines restrictions

Cardinality conventions (aligned with ontology-cdm-p1/p2):
  exactly 1 → sh:node :ExactlyOneShape
  min 1     → sh:node :MinOneShape
  max 1     → sh:node :MaxOneShape
  other     → explicit sh:minCount / sh:maxCount
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
SH = Namespace("http://www.w3.org/ns/shacl#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
TIME = Namespace("http://www.w3.org/2006/time#")
SCHEMA = Namespace("http://schema.org/")

PREFIXES = """@prefix : <https://w3id.org/citydata/part3/v1/> .
@prefix cdm3: <https://w3id.org/citydata/part3/v1/> .
@prefix cdm1: <https://w3id.org/citydata/part1/v1/> .
@prefix cdm2: <https://w3id.org/citydata/part2/v1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix vann: <http://purl.org/vocab/vann/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix geo: <http://www.opengis.net/ont/geosparql#> .
@prefix time: <http://www.w3.org/2006/time#> .
"""


def qname(term, nsm) -> str:
    if isinstance(term, URIRef):
        s = str(term)
        if s.startswith(str(NS)):
            local = s[len(str(NS)) :]
            if local and "/" not in local and "#" not in local:
                return f":{local}"
            return f"<{s}>"
        prefix_map = [
            ("cdm1:", str(CDM1)),
            ("cdm2:", str(CDM2)),
            ("geo:", str(GEO)),
            ("time:", str(TIME)),
            ("xsd:", str(XSD)),
            ("owl:", str(OWL)),
            ("rdf:", str(RDF)),
            ("rdfs:", str(RDFS)),
            ("skos:", str(SKOS)),
            ("sh:", str(SH)),
            ("schema:", str(SCHEMA)),
        ]
        for pfx, iri in prefix_map:
            if s.startswith(iri):
                local = s[len(iri) :]
                if local and "/" not in local and "#" not in local:
                    return pfx + local
                return f"<{s}>"
        try:
            return term.n3(nsm)
        except Exception:
            return f"<{s}>"
    if isinstance(term, Literal):
        return term.n3(nsm)
    return str(term)


def is_datatype(term) -> bool:
    if not isinstance(term, URIRef):
        return False
    s = str(term)
    return s.startswith(str(XSD)) or s.startswith(str(RDF))


def union_members(g: Graph, node) -> list[URIRef] | None:
    if not isinstance(node, BNode):
        return None
    col = g.value(node, OWL.unionOf)
    if col is None:
        return None
    members = list(Collection(g, col))
    if members and all(isinstance(m, URIRef) for m in members):
        return members
    return None


def pattern_stem(path: Path) -> str:
    """TransportNetworkPattern.ttl → TransportNetwork"""
    name = path.stem
    if name.endswith("Pattern"):
        return name[: -len("Pattern")]
    return name


def ontology_iri(g: Graph) -> URIRef | None:
    ontos = sorted(g.subjects(RDF.type, OWL.Ontology), key=str)
    return ontos[0] if ontos else None


def extract_restrictions(g: Graph) -> dict[URIRef, dict[URIRef, dict]]:
    """
    Return {class: {property: {filler, is_datatype, min_c, max_c, union_members}}}.
    Multiple restrictions on the same property are merged.
    """
    shapes: dict[URIRef, dict[URIRef, dict]] = defaultdict(dict)

    for cls in sorted(
        (
            s
            for s in g.subjects(RDF.type, OWL.Class)
            if isinstance(s, URIRef) and str(s).startswith(str(NS)) and "/" not in str(s)[len(str(NS)) :]
        ),
        key=str,
    ):
        by_prop: dict[URIRef, dict] = {}
        for super_ in g.objects(cls, RDFS.subClassOf):
            if not isinstance(super_, BNode) or (super_, RDF.type, OWL.Restriction) not in g:
                continue
            on_prop = g.value(super_, OWL.onProperty)
            if on_prop is None or not isinstance(on_prop, URIRef):
                continue

            on_class = g.value(super_, OWL.onClass)
            all_from = g.value(super_, OWL.allValuesFrom)
            on_data = g.value(super_, OWL.onDataRange)
            qcard = g.value(super_, OWL.qualifiedCardinality)
            minq = g.value(super_, OWL.minQualifiedCardinality)
            maxq = g.value(super_, OWL.maxQualifiedCardinality)
            card = g.value(super_, OWL.cardinality)

            filler = None
            is_dt = False
            union = None
            for candidate in (on_class, all_from, on_data):
                if candidate is None:
                    continue
                if isinstance(candidate, URIRef):
                    filler = candidate
                    is_dt = is_datatype(candidate) or on_data is not None
                    break
                union = union_members(g, candidate)
                if union is not None:
                    break

            min_c = max_c = None
            if qcard is not None:
                min_c = max_c = int(qcard)
            if card is not None:
                min_c = max_c = int(card)
            if minq is not None:
                min_c = int(minq)
            if maxq is not None:
                max_c = int(maxq)

            if filler is None and union is None and min_c is None and max_c is None:
                continue

            entry = by_prop.setdefault(
                on_prop,
                {
                    "filler": None,
                    "is_datatype": False,
                    "union": None,
                    "min_c": None,
                    "max_c": None,
                },
            )
            if filler is not None and entry["filler"] is None:
                entry["filler"] = filler
                entry["is_datatype"] = is_dt
            if union is not None and entry["union"] is None:
                entry["union"] = union
            if min_c is not None:
                entry["min_c"] = min_c if entry["min_c"] is None else max(entry["min_c"], min_c)
            if max_c is not None:
                entry["max_c"] = max_c if entry["max_c"] is None else min(entry["max_c"], max_c)

        if by_prop:
            shapes[cls] = by_prop
    return shapes


def cardinality_node(min_c, max_c) -> str | None:
    if min_c == 1 and max_c == 1:
        return ":ExactlyOneShape"
    if min_c == 1 and max_c is None:
        return ":MinOneShape"
    if min_c is None and max_c == 1:
        return ":MaxOneShape"
    return None


def write_property_block(nsm, on_prop, entry, is_last: bool) -> list[str]:
    lines = ["    sh:property [", f"        sh:path {qname(on_prop, nsm)} ;"]
    node = cardinality_node(entry["min_c"], entry["max_c"])
    if node is not None:
        lines.append(f"        sh:node {node} ;")
    else:
        if entry["min_c"] is not None:
            lines.append(f'        sh:minCount "{entry["min_c"]}"^^xsd:integer ;')
        if entry["max_c"] is not None:
            lines.append(f'        sh:maxCount "{entry["max_c"]}"^^xsd:integer ;')

    if entry["union"] is not None:
        lines.append("        sh:or (")
        for m in entry["union"]:
            lines.append(f"            [ sh:class {qname(m, nsm)} ]")
        lines.append("        ) ;")
    elif entry["filler"] is not None:
        key = "sh:datatype" if entry["is_datatype"] else "sh:class"
        lines.append(f"        {key} {qname(entry['filler'], nsm)} ;")

    # Drop trailing semicolon on last constraint line inside the blank node
    lines[-1] = lines[-1].rstrip(" ;")
    sep = " ." if is_last else " ;"
    lines.append(f"    ]{sep}")
    return lines


def write_core_shacl() -> str:
    return (
        PREFIXES
        + """
:CoreSHACL
    rdf:type owl:Ontology ;
    dcterms:title "City Data Model Part 3 - Core - SHACL constraints" ;
    skos:definition "SHACL validation shapes for the Core pattern module, including reusable cardinality shapes." ;
    vann:preferredNamespaceUri "https://w3id.org/citydata/part3/v1/" ;
    vann:preferredNamespacePrefix "cdm3" ;
    owl:imports <https://w3id.org/citydata/part3/v1/Core/> .

:ExactlyOneShape
    rdf:type sh:NodeShape ;
    sh:minCount 1 ;
    sh:maxCount 1 .

:MinOneShape
    rdf:type sh:NodeShape ;
    sh:minCount 1 .

:MaxOneShape
    rdf:type sh:NodeShape ;
    sh:maxCount 1 .
"""
    )


def write_pattern_shacl(pattern_path: Path, g: Graph, shapes: dict) -> str:
    nsm = Graph().namespace_manager
    for pfx, ns in (
        ("", NS),
        ("cdm1", CDM1),
        ("cdm2", CDM2),
        ("geo", GEO),
        ("time", TIME),
        ("xsd", XSD),
        ("sh", SH),
        ("owl", OWL),
        ("rdf", RDF),
        ("rdfs", RDFS),
        ("skos", SKOS),
    ):
        nsm.bind(pfx, ns, override=True)

    stem = pattern_stem(pattern_path)
    shacl_name = f"{stem}SHACL"
    title = f"City Data Model Part 3 - {stem} Pattern - SHACL constraints"
    definition = f"SHACL validation shapes for the {stem} Pattern module."
    ont = ontology_iri(g)
    import_pattern = f"<{ont}>" if ont is not None else f":{pattern_path.stem}"

    parts = [PREFIXES, "\n"]
    parts.append(
        f""":{shacl_name}
    rdf:type owl:Ontology ;
    dcterms:title "{title}" ;
    skos:definition "{definition}" ;
    vann:preferredNamespaceUri "https://w3id.org/citydata/part3/v1/" ;
    vann:preferredNamespacePrefix "cdm3" ;
    owl:imports {import_pattern} ;
    owl:imports :CoreSHACL .

"""
    )

    for cls in sorted(shapes, key=str):
        local = str(cls)[len(str(NS)) :]
        props = shapes[cls]
        prop_items = sorted(props.items(), key=lambda kv: str(kv[0]))
        lines = [
            f":{local}Shape",
            "    rdf:type sh:NodeShape ;",
            f"    sh:targetClass :{local} ;",
        ]
        for i, (on_prop, entry) in enumerate(prop_items):
            lines.extend(write_property_block(nsm, on_prop, entry, is_last=(i == len(prop_items) - 1)))
        parts.append("\n".join(lines) + "\n\n")

    return "".join(parts).rstrip() + "\n"


def update_master_imports(shacl_names: list[str]) -> None:
    """Ensure 5087-3.ttl imports each SHACL module."""
    master = DOCS / "5087-3.ttl"
    if not master.exists():
        return
    text = master.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Remove existing SHACL imports so regeneration is idempotent
    lines = [ln for ln in lines if "SHACL" not in ln or "owl:imports" not in ln]

    # Find last owl:imports line to append after
    last_import_idx = None
    for i, ln in enumerate(lines):
        if "owl:imports" in ln:
            last_import_idx = i
    if last_import_idx is None:
        return

    # Ensure the previous last import ends with ; then add SHACL imports
    # Normalize terminator on the last existing import
    insert_at = last_import_idx + 1
    # Make sure line at last_import_idx ends with ;
    if lines[last_import_idx].rstrip().endswith("."):
        lines[last_import_idx] = lines[last_import_idx].rstrip()[:-1].rstrip() + " ;"

    new_imports = [f"    owl:imports                  :{name} ;" for name in shacl_names]
    if new_imports:
        new_imports[-1] = new_imports[-1][:-1] + "."
    lines[insert_at:insert_at] = new_imports
    master.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    written = []

    core_path = DOCS / "CoreSHACL.ttl"
    core_path.write_text(write_core_shacl(), encoding="utf-8")
    written.append(core_path)
    print(f"Wrote {core_path.name}")

    shacl_ontology_names = ["CoreSHACL"]
    for pattern_path in sorted(DOCS.glob("*Pattern.ttl")):
        if pattern_path.name == "CorePattern.ttl":
            continue
        g = Graph()
        g.parse(pattern_path)
        shapes = extract_restrictions(g)
        if not shapes:
            print(f"Skip {pattern_path.name}: no restrictions")
            continue
        stem = pattern_stem(pattern_path)
        out = DOCS / f"{stem}SHACL.ttl"
        out.write_text(write_pattern_shacl(pattern_path, g, shapes), encoding="utf-8")
        written.append(out)
        shacl_ontology_names.append(f"{stem}SHACL")
        print(f"Wrote {out.name} ({len(shapes)} shapes)")

    update_master_imports(shacl_ontology_names)
    print(f"Updated 5087-3.ttl imports ({len(shacl_ontology_names)} SHACL modules)")

    # Validate parse
    for path in written + [DOCS / "5087-3.ttl"]:
        Graph().parse(path)
        print(f"  OK parse {path.name}")


if __name__ == "__main__":
    main()
