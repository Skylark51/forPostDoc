from __future__ import annotations
import hashlib, re
from pathlib import Path
from .models import GaussianRecord

SCF_RE = re.compile(r"SCF Done:\s+E\([^)]+\)\s+=\s+(-?\d+\.\d+)")
CHARGE_MULT_RE = re.compile(r"Charge\s*=\s*(-?\d+)\s+Multiplicity\s*=\s*(\d+)")
ROUTE_RE = re.compile(r"^\s*#.*$", re.MULTILINE)
ATOMIC_SYMBOLS = {1:"H",6:"C",7:"N",8:"O",9:"F",14:"Si",15:"P",16:"S",17:"Cl",25:"Mn",26:"Fe",27:"Co",28:"Ni",29:"Cu",34:"Se",52:"Te",58:"Ce"}

def _last_electronic_energy(text: str) -> float | None:
    vals = [float(x) for x in SCF_RE.findall(text)]
    return vals[-1] if vals else None

def _job_types(route: str) -> list[str]:
    r = route.lower(); jobs=[]
    for token,name in [("opt","Opt"),("freq","Freq"),("irc","IRC"),("td","TD-DFT"),("stable","Stable"),("scan","Scan")]:
        if token in r and name not in jobs: jobs.append(name)
    if "opt=(ts" in r or "opt=ts" in r or "ts," in r: jobs.append("TS")
    return jobs or ["SPE"]

def _method_basis(route: str) -> str | None:
    route=" ".join(route.split()); m=re.search(r"([uUrR]?[A-Za-z0-9()+\-]+/[A-Za-z0-9()+\-*,]+)", route)
    return m.group(1) if m else None

def _last_orientation(text: str) -> str | None:
    starts=[m.start() for m in re.finditer(r"Standard orientation:", text)]
    if not starts: starts=[m.start() for m in re.finditer(r"Input orientation:", text)]
    if not starts: return None
    lines=text[starts[-1]:].splitlines(); dash=[i for i,l in enumerate(lines) if set(l.strip()) == {"-"}]
    if len(dash) < 3: return None
    atoms=[]
    for line in lines[dash[1]+1:dash[2]]:
        parts=line.split()
        if len(parts)<6: continue
        try: znum=int(parts[1]); x,y,z=map(float,parts[-3:])
        except ValueError: continue
        atoms.append((ATOMIC_SYMBOLS.get(znum,str(znum)),x,y,z))
    if not atoms: return None
    body="\n".join(f"{s:<2} {x: .9f} {y: .9f} {z: .9f}" for s,x,y,z in atoms)
    return f"{len(atoms)}\nExtracted from final Gaussian orientation\n{body}\n"

def parse_gaussian(path: Path, project_key: str) -> GaussianRecord:
    path=Path(path); raw=path.read_bytes(); text=raw.decode("utf-8",errors="replace")
    route_match=ROUTE_RE.search(text); route=route_match.group(0) if route_match else ""; cm=CHARGE_MULT_RE.findall(text); charge=multiplicity=None
    if cm: charge,multiplicity=map(int,cm[-1])
    return GaussianRecord(project_key=project_key, source_path=path.resolve(), filename=path.name, sha256=hashlib.sha256(raw).hexdigest(), normal_termination="Normal termination of Gaussian" in text, charge=charge, multiplicity=multiplicity, method_basis=_method_basis(route), job_types=_job_types(route), electronic_energy_hartree=_last_electronic_energy(text), xyz=_last_orientation(text), raw_metadata={"route":route.strip()})
