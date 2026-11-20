from scopeshift.mutations import campaign


def test_all_targeted_mutations(tmp_path):
    result = campaign(tmp_path)
    assert len(result["gateway"]) == 11
    assert len(result["grader"]) == 9
    assert all(item["status"] == "killed" for item in result["gateway"]), result
    assert all(item["status"] == "killed" for item in result["grader"]), result
