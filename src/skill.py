import random
import damage

# TODO: Verify these values
SHORT_DELAY = 0.75
LONG_DELAY = 1.3 # X-Pot delay
GCD_DELAY = 0.9

# Data on auras
class Aura:
    name = ""
    duration = 0
    has_snapshot = False

    @classmethod
    def _tick(cls, source, target):
        pass

    # TO CONSIDER: LOGGING MULTIHIT MOVES
    # add_potency should probably add the log?
    # Or maybe tick should just return an array of results?
    # append source, target to all of them
    # log to source and target
    # source and target should log only if logging is enabled for them
    @classmethod
    def tick(cls, source, target):
        return cls._tick(source, target)

    @classmethod
    def potency_modifier(cls):
        return {}

class SilenceAura(Aura):
    name = "Silence"
    duration = 1 # Some moves may give the same aura but have different durations

class InternalReleaseAura(Aura):
    name = "Internal Release"
    duration = 15

    @classmethod
    def potency_modifier(cls):
        return {
            "critical_hit_rate_add": 0.10
        }

class BloodForBloodAura(Aura):
    name = "Blood for Blood"
    duration = 20

    @classmethod
    def potency_modifier(cls):
        return {
            "potency_multiply": 1.10
        }

class RagingStrikesAura(Aura):
    name = "Raging Strikes"
    duration = 20

    @classmethod
    def potency_modifier(cls):
        return {
            "potency_multiply": 1.20
        }

class HawksEyeAura(Aura):
    name = "Hawk's Eye"
    duration = 20

    @classmethod
    def potency_modifier(cls):
        return {
            "potency_multiply": 1.13 # about
        }

class BarrageAura(Aura):
    name = "Barrage"
    duration = 10

class StraightShotAura(Aura):
    name = "Straight Shot"
    duration = 20

    @classmethod
    def potency_modifier(cls):
        return {
            "critical_hit_rate_add": 0.10
        }

class StraighterShotAura(Aura):
    name = "Straighter Shot"
    duration = 10

class XPotionOfDexterityAura(Aura):
    name = "Medicated"
    duration = 15

    @classmethod
    def potency_modifier(cls):
        return {
            "potency_multiply": 1.11 # about. Hawk's Eye also affects X-Pot bonuses (i.e. it's multiplicative)
        }

class FlamingArrowAura(Aura):
    name = "Flaming Arrow"
    duration = 30
    has_snapshot = True

    @classmethod
    def _tick(cls, source, target):
        result = damage.calculate_dot_potency(30, source, target, FlamingArrowAura)
        target.add_potency(result)

class VenomousBiteAura(Aura):
    name = "Venomous Bite"
    duration = 18
    has_snapshot = True

    @classmethod
    def _tick(cls, source, target):
        result = damage.calculate_dot_potency(35, source, target, VenomousBiteAura)
        target.add_potency(result)
        if result["critical_hit"] is True and random.random() < 0.5:
            source.reset_cooldown(Bloodletter)

class WindbiteAura(Aura):
    name = "Windbite"
    duration = 18
    has_snapshot = True

    @classmethod
    def _tick(cls, source, target):
        result = damage.calculate_dot_potency(45, source, target, WindbiteAura)
        target.add_potency(result)
        if result["critical_hit"] is True and random.random() < 0.5:
            source.reset_cooldown(Bloodletter)

# Data on skills
class Skill:
    name = ""
    animation_lock = 0
    cooldown = 0
    tp_cost = 0
    is_off_gcd = False

    @classmethod
    def _use(cls, source, target):
        pass

    @classmethod
    def use(cls, source, target):
        return cls._use(source, target)

class InternalRelease(Skill):
    name = "Internal Release"
    animation_lock = SHORT_DELAY
    cooldown = 60
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_aura(InternalReleaseAura)

class BloodForBlood(Skill):
    name = "Blood for Blood"
    animation_lock = SHORT_DELAY
    cooldown = 80
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_aura(BloodForBloodAura)

class RagingStrikes(Skill):
    name = "Raging Strikes"
    animation_lock = SHORT_DELAY
    cooldown = 120
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_aura(RagingStrikesAura)

class HawksEye(Skill):
    name = "Hawk's Eye"
    animation_lock = SHORT_DELAY
    cooldown = 90
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_aura(HawksEyeAura)

class Barrage(Skill):
    name = "Barrage"
    animation_lock = SHORT_DELAY
    cooldown = 90
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_aura(BarrageAura)

class XPotionOfDexterity(Skill):
    name = "X-Potion of Dexterity"
    animation_lock = LONG_DELAY
    cooldown = 270
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_aura(XPotionOfDexterityAura)

class HeavyShot(Skill):
    name = "Heavy Shot"
    animation_lock = GCD_DELAY
    tp_cost = 60

    @classmethod
    def _use(cls, source, target):
        if random.random() < 0.2:
            source.add_aura(StraighterShotAura)
        target.add_potency(damage.calculate_potency(150, source))

class StraightShot(Skill):
    name = "Straight Shot"
    animation_lock = GCD_DELAY
    tp_cost = 70

    @classmethod
    def _use(cls, source, target):
        if source.has_aura(StraighterShotAura):
            source.remove_aura(StraighterShotAura)
            target.add_potency(damage.calculate_potency(140, source, guaranteed_critical=True))
        else:
            target.add_potency(damage.calculate_potency(140, source))
        source.add_aura(StraightShotAura)

class VenomousBite(Skill):
    name = "Venomous Bite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @classmethod
    def _use(cls, source, target):
        target.add_potency(damage.calculate_potency(100, source))
        target.add_aura(VenomousBiteAura, source)

class Windbite(Skill):
    name = "Windbite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @classmethod
    def _use(cls, source, target):
        target.add_potency(damage.calculate_potency(60, source))
        target.add_aura(WindbiteAura, source)

class FlamingArrow(Skill): 
    name = "Flaming Arrow"
    animation_lock = SHORT_DELAY
    cooldown = 60
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        target.add_aura(FlamingArrowAura, source)

class BluntArrow(Skill):
    name = "Blunt Arrow"
    animation_lock = SHORT_DELAY
    cooldown = 30
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        target.add_potency(damage.calculate_potency(50, source))
        target.add_aura(SilenceAura, source)

class RepellingShot(Skill):
    name = "Repelling Shot"
    animation_lock = SHORT_DELAY
    cooldown = 30
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        target.add_potency(damage.calculate_potency(80, source))

class Bloodletter(Skill):
    name = "Bloodletter"
    animation_lock = SHORT_DELAY
    cooldown = 15
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        target.add_potency(damage.calculate_potency(150, source))

class Invigorate(Skill):
    name = "Invigorate"
    animation_lock = SHORT_DELAY
    cooldown = 120
    is_off_gcd = True

    @classmethod
    def _use(cls, source, target):
        source.add_tp(400)

class AutoAttack(Skill):
    name = "Auto Attack"
    animation_lock = 0

    @classmethod
    def _use(cls, source, target):
        auto_attacks = 1
        if source.has_aura(BarrageAura):
            auto_attacks = 3

        for i in xrange(0, auto_attacks):
            target.add_potency(damage.calculate_potency(88.7, source)) # TODO: Use actual damage models to calculate damage?
