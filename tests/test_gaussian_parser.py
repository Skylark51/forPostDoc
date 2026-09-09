from ccra.gaussian_parser import parse_gaussian
SAMPLE=""" Gaussian 16
 # opt freq ub3lyp/def2SVP nosymm
 Charge = 0 Multiplicity = 3
 SCF Done:  E(UB3LYP) =  -100.123456789     A.U.
 Standard orientation:
 ---------------------------------------------------------------------
 Center     Atomic      Atomic             Coordinates (Angstroms)
 Number     Number       Type             X           Y           Z
 ---------------------------------------------------------------------
      1          26           0        0.000000    0.000000    0.000000
      2           7            0        0.000000    0.000000    1.700000
 ---------------------------------------------------------------------
 Normal termination of Gaussian 16
"""
def test_parse_core_fields(tmp_path):
    p=tmp_path/"3-test-opt-freq.out"; p.write_text(SAMPLE); r=parse_gaussian(p,"feno6")
    assert r.normal_termination and r.charge==0 and r.multiplicity==3
    assert abs(r.electronic_energy_hartree+100.123456789)<1e-12
    assert "Opt" in r.job_types and "Freq" in r.job_types
    assert "Fe" in r.xyz and "N" in r.xyz
