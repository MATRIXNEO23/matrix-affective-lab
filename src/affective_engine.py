from __future__ import annotations

# Source provenance: FAtiMA Toolkit Apache-2.0 commit 56b7cbd992f953cfe21a7b12cb1a0e6cdf6ccf9f;
# Cognitiv MIT commit f3aad875a77a3c7c522781e03acbb1944c3ab25c; Alma.Net MIT commit
# 55b0475abdd077f145ed90575b435111c288454e. Matrix extension: causal persistent ledger.
import math
from dataclasses import dataclass,field
from typing import Dict,Optional
@dataclass(frozen=True)
class EmotionalImpulse: emotion_type:str;intensity:float;cause_id:str;target_id:Optional[str]=None;appraisal_channel:str="generic"
@dataclass
class EmotionDisposition: threshold:float=.05;half_life:float=15.
@dataclass(frozen=True)
class OceanProfile: openness:float=0.;conscientiousness:float=0.;extroversion:float=0.;agreeableness:float=0.;neuroticism:float=0.
@dataclass(frozen=True)
class AffectiveProfile: reactivity:float=1.;positive_reactivity:float=1.;negative_reactivity:float=1.;recovery_scale:float=1.;persistent_step:float=.05;mood_bias_strength:float=.15;mood_half_life:Optional[float]=None;ocean:Optional[OceanProfile]=None
@dataclass(frozen=True)
class AffectiveConfig: half_life_decay_constant:float=.5;emotion_influence_on_mood_factor:float=.3;mood_influence_on_emotion_factor:float=.3;minimum_mood_for_influence:float=.05;emotional_half_life_decay_time:float=15.;mood_half_life_decay_time:float=60.;extinction_threshold:float=.01
@dataclass
class EmotionState: emotions:Dict[str,float]=field(default_factory=dict);valence:float=0.;arousal:float=0.;dominance:float=0.;virtual_emotion_intensity:float=0.;mood_valence:float=0.;mood_arousal:float=0.
@dataclass
class PersistentAffect: trust:float=.5;attachment:float=0.;affection:float=0.;attraction:float=0.;resentment:float=0.;respect:float=.5;admiration:float=0.;aversion:float=0.
@dataclass
class _Contribution: emotion_type:str;intensity_at_t0:float;tick_t0:float;threshold:float;decay_multiplier:float;source_potential:float
class AffectiveEngine:
 POSITIVE={"joy","hope","relief","satisfaction","admiration","pride","gratitude","gratification","love","liking","happy-for","gloating","affection"};NEGATIVE={"distress","fear","fears-confirmed","disappointment","anger","reproach","shame","remorse","resentment","hate","disliking","pity","aversion"}
 REPAIR_TRUST={"gratitude","relief","satisfaction"};PERSISTENT_EFFECTS={"joy","relief","satisfaction","love","liking","gratitude","happy-for","affection","admiration","pride","gratification","anger","reproach","resentment","disappointment","fears-confirmed","hate","disliking","aversion"}
 ALMA_PAD={"admiration":(.5,.3,-.2),"anger":(-.51,.59,.25),"disliking":(-.4,.2,.1),"disappointment":(-.3,.1,-.4),"distress":(-.4,-.2,-.5),"fear":(-.64,.60,-.43),"fears-confirmed":(-.5,-.3,-.7),"gloating":(.3,-.3,-.1),"gratification":(.6,.5,.4),"gratitude":(.4,.2,-.3),"happy-for":(.4,.2,.2),"hate":(-.6,.6,.3),"hope":(.2,.2,-.1),"joy":(.4,.2,.1),"liking":(.4,.16,-.24),"love":(.3,.1,.2),"pity":(-.4,-.2,-.5),"pride":(.4,.3,.3),"relief":(.2,-.3,.4),"remorse":(-.3,.1,-.6),"reproach":(-.3,-.1,.4),"resentment":(-.2,-.3,-.2),"satisfaction":(.3,-.2,.4),"shame":(-.3,.1,-.6)}
 def __init__(self,dispositions=None,profile=None,config=None):self.state=EmotionState();self.dispositions=dispositions or {};self.profile=profile or AffectiveProfile();self.config=config or AffectiveConfig();self.persistent_affect={};self._contributions={};self._persistent_ledger={};self._time=0.;self._mood_at_t0=0.;self._mood_tick_t0=0.
 def disposition(self,e):return self.dispositions.get(e,EmotionDisposition())
 @staticmethod
 def ocean_to_pad(o):return tuple(max(-1.,min(1.,x)) for x in (.21*o.extroversion+.59*o.agreeableness+.19*o.neuroticism,.15*o.openness+.30*o.agreeableness-.57*o.neuroticism,.25*o.openness+.17*o.conscientiousness+.60*o.extroversion-.32*o.agreeableness))
 def contribution_for(self,cause_id,appraisal_channel,target_id):
  c=self._contributions.get((cause_id,appraisal_channel,target_id));return None if c is None else(c.emotion_type,self._decayed_contribution(c,self._time))
 def apply_impulse(self,i):
  slot=(i.cause_id,i.appraisal_channel,i.target_id);prev=self._contributions.get(slot);pled=self._persistent_ledger.get(slot);raw=self._profiled_intensity(i.emotion_type,i.intensity)
  if prev and prev.emotion_type==i.emotion_type and math.isclose(prev.source_potential,raw,abs_tol=1e-12):return False
  if pled and pled[0]==i.emotion_type and math.isclose(pled[2],raw,abs_tol=1e-12):return False
  if prev:del self._contributions[slot];self._recompute_emotion(prev.emotion_type)
  if pled:del self._persistent_ledger[slot];self._recompute_persistent(i.target_id)
  d=self.disposition(i.emotion_type);th=self._clamp(d.threshold)
  if raw<=th:self._update_dimensions();return prev is not None or pled is not None
  pot=self._determine_potential(i.emotion_type,raw)
  if pot<=th:self._update_dimensions();return prev is not None or pled is not None
  intensity=self._clamp(pot-th);self._contributions[slot]=_Contribution(i.emotion_type,intensity,self._time,th,self._fatima_decay_multiplier(d),raw);self._recompute_emotion(i.emotion_type)
  if i.target_id and i.emotion_type in self.PERSISTENT_EFFECTS:self._persistent_ledger[slot]=(i.emotion_type,intensity,raw);self._recompute_persistent(i.target_id)
  if prev is None and pled is None and self._influences_mood(i.emotion_type):self._update_mood_from_new_emotion(i.emotion_type,intensity)
  self._update_dimensions();return True
 def decay(self,dt):
  if dt<=0:return
  self._time+=dt;self._decay_mood_to(self._time);dead=[];touched=set()
  for slot,c in self._contributions.items():
   touched.add(c.emotion_type)
   if self._decayed_contribution(c,self._time)<=self.config.extinction_threshold:dead.append(slot)
  for slot in dead:touched.add(self._contributions[slot].emotion_type);del self._contributions[slot]
  for e in touched:self._recompute_emotion(e)
  self._update_dimensions()
 def reinforce(self,cause_id,appraisal_channel,target_id,potential):
  slot=(cause_id,appraisal_channel,target_id);c=self._contributions.get(slot)
  if c is None:return False
  cur=self._decayed_contribution(c,self._time);p=self._clamp(potential);a=(cur+c.threshold)*10.;b=p*10.;pivot=max(a,b);r=min(1.,(pivot+math.log(math.exp(a-pivot)+math.exp(b-pivot)))/10.);ni=self._clamp(r-c.threshold);self._contributions[slot]=_Contribution(c.emotion_type,ni,self._time,c.threshold,c.decay_multiplier,max(c.source_potential,p))
  if target_id and c.emotion_type in self.PERSISTENT_EFFECTS:self._persistent_ledger[slot]=(c.emotion_type,ni,max(c.source_potential,p));self._recompute_persistent(target_id)
  self._recompute_emotion(c.emotion_type);self._update_dimensions();return True
 def _recompute_persistent(self,entity):
  if not entity:return
  raw={"trust":.5,"attachment":0.,"affection":0.,"attraction":0.,"resentment":0.,"respect":.5,"admiration":0.,"aversion":0.};step=max(0.,self.profile.persistent_step);seen=False
  for (cause,ch,target),(e,intensity,source) in self._persistent_ledger.items():
   if target!=entity:continue
   seen=True;s=intensity*step
   if e in {"joy","relief","satisfaction","love","liking","gratitude","happy-for","affection"}:raw["affection"]=self._clamp(raw["affection"]+s);raw["attachment"]=self._clamp(raw["attachment"]+s*.5)
   if e in {"admiration","pride","gratitude","gratification"}:raw["admiration"]=self._clamp(raw["admiration"]+s);raw["respect"]=self._clamp(raw["respect"]+s*.5)
   if e in {"anger","reproach","resentment","disappointment","fears-confirmed"}:raw["resentment"]=self._clamp(raw["resentment"]+s);raw["trust"]=self._clamp(raw["trust"]-s)
   if e in self.REPAIR_TRUST:raw["trust"]=self._clamp(raw["trust"]+s*.3);raw["resentment"]=self._clamp(raw["resentment"]-s*.4)
   if e in {"hate","disliking","aversion"}:raw["aversion"]=self._clamp(raw["aversion"]+s)
  if not seen:
   if entity in self.persistent_affect:self.persistent_affect[entity]=PersistentAffect()
   return
  self.persistent_affect[entity]=PersistentAffect(**raw)
 def _fatima_decay_multiplier(self,d):return self.config.emotional_half_life_decay_time/max(.01,d.half_life*max(.01,self.profile.recovery_scale))
 def _decayed_contribution(self,c,t):return c.intensity_at_t0*math.exp(math.log(self.config.half_life_decay_constant)/max(.01,self.config.emotional_half_life_decay_time)*c.decay_multiplier*max(0.,t-c.tick_t0))
 def _determine_potential(self,e,p):return max(0.,p+self._emotion_valence(e)*(self.state.mood_valence*self.config.mood_influence_on_emotion_factor))
 def _set_mood(self,v):v=max(-1.,min(1.,v));v=0. if abs(v)<self.config.minimum_mood_for_influence else v;self.state.mood_valence=v;self._mood_at_t0=v;self._mood_tick_t0=self._time
 def _update_mood_from_new_emotion(self,e,i):self._set_mood(self.state.mood_valence+self._emotion_valence(e)*(i*self.config.emotion_influence_on_mood_factor))
 def _decay_mood_to(self,t):
  if self._mood_at_t0==0:self.state.mood_valence=0.;return
  hl=self.profile.mood_half_life or self.config.mood_half_life_decay_time;v=self._mood_at_t0*math.exp(math.log(self.config.half_life_decay_constant)/max(.01,hl)*max(0.,t-self._mood_tick_t0))
  if abs(v)<self.config.minimum_mood_for_influence:self.state.mood_valence=0.;self._mood_at_t0=0.;self._mood_tick_t0=0.
  else:self.state.mood_valence=v
 def _recompute_emotion(self,e):
  vals=[self._decayed_contribution(c,self._time) for c in self._contributions.values() if c.emotion_type==e]
  if not vals:self.state.emotions.pop(e,None);return
  r=1.
  for v in vals:r*=1.-self._clamp(v)
  self.state.emotions[e]=self._clamp(1.-r)
 def _update_dimensions(self):
  if not self.state.emotions:self.state.valence=self.state.arousal=self.state.dominance=self.state.virtual_emotion_intensity=0.;return
  p=a=d=ti=0.;mapped=0
  for e,i in self.state.emotions.items():
   pad=self.ALMA_PAD.get(e)
   if pad is None:continue
   p+=pad[0];a+=pad[1];d+=pad[2];ti+=i;mapped+=1
  if not mapped:self.state.valence=self.state.arousal=self.state.dominance=self.state.virtual_emotion_intensity=0.;return
  self.state.valence=max(-1.,min(1.,p));self.state.arousal=max(-1.,min(1.,a));self.state.dominance=max(-1.,min(1.,d));self.state.virtual_emotion_intensity=self._clamp(ti/mapped)
 def _profiled_intensity(self,e,v):s=self.profile.reactivity*(self.profile.positive_reactivity if e in self.POSITIVE else self.profile.negative_reactivity if e in self.NEGATIVE else 1.);return self._clamp(v*max(0.,s))
 def _emotion_valence(self,e):return 1. if e in self.POSITIVE else -1. if e in self.NEGATIVE else 0.
 def _influences_mood(self,e):return e not in {"hope","fear"}
 @staticmethod
 def _clamp(v):return max(0.,min(1.,v))
 def snapshot(self):return {"emotions":dict(self.state.emotions),"valence":self.state.valence,"arousal":self.state.arousal,"dominance":self.state.dominance,"virtual_emotion_intensity":self.state.virtual_emotion_intensity,"default_personality_pad":self.ocean_to_pad(self.profile.ocean) if self.profile.ocean else None,"mood_valence":self.state.mood_valence,"mood_arousal":self.state.mood_arousal,"persistent_affect":{k:vars(v).copy() for k,v in self.persistent_affect.items()}}