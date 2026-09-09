from ccra.reaction_coordinate.templates import branched_template,circular_template,linear_template,two_branch_template

def test_templates_are_project_bound_and_usable():
    for factory in [linear_template,circular_template,branched_template,two_branch_template]:
        d=factory("deformylation","Main")
        assert d.project_key=="deformylation" and d.module_name=="Main"
        assert d.nodes and d.edges
        assert all((n.x,n.y)!=(0.0,0.0) for n in d.nodes)
