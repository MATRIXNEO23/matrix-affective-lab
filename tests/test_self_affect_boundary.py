from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def test_self_pride_does_not_create_external_persistent_entity():
    p=MatrixAffectivePrototype();p.process(AffectiveStimulus(id="self-good",category="action",actor_id="self",standard_compliance=.8));assert "self" not in p.affect.persistent_affect
