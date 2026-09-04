from src.prototype import AffectiveStimulus, MatrixAffectivePrototype


def emotion(des_self,des_other):
    p=MatrixAffectivePrototype();t=p.process(AffectiveStimulus(id="x",category="event",goal_congruence=des_self,desirability_for_other=des_other,other_id="alice"));return [i.emotion_type for i in t.appraisal.impulses]

def test_happy_for():assert "happy-for" in emotion(.5,.8)
def test_gloating():assert "gloating" in emotion(.5,-.8)
def test_resentment():assert "resentment" in emotion(-.5,.8)
def test_pity():assert "pity" in emotion(-.5,-.8)
