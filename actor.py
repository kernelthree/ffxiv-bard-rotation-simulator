import sys
from skill import *

class AuraTimer:
    def __init__(self, duration=0, snapshot=[]):
        self.duration = duration
        self.snapshot = snapshot

# Dumb slate for a character or enemy.
class Actor:
    def __init__(self, job):
        self.job = job

        self.cooldowns = {}
        self.auras = {}         # keys are (aura class, source actor)
        self.gcd_timer = 0      # time until next GCD
        self.aa_timer = 0       # time until next auto attack
        self.animation_lock = 0 # time until animation lock is finished
        self.tp = 1000
        self.potency = 0 # Damage inflicted on actor in terms of potency.
                         # Actual damage = self.potency * self.damage_per_potency

        # Static parameters that should be passed into the actor
        self.base_critical_hit_rate = 0.197586
        self.aa_cooldown = 3.04
        self.gcd_cooldown = 2.45
        self.damage_per_potency = 2.4888 # TODO: associate potency damage on enemies with source

        # For time of interest purposes to check if a cooldown has been reset.
        self.check_now = True

    def snapshot(self):
        return self.auras.keys()

    # Adds an aura to the actor.
    def add_aura(self, aura, source=None):
        if source is None:
            source = self

        aura_timer = None
        if aura.has_snapshot:
            aura_timer = AuraTimer(aura.duration, source.snapshot())
        else:
            aura_timer = AuraTimer(aura.duration)
        self.auras[(aura, source)] = aura_timer

    def remove_aura(self, aura, source=None):
        if source is None:
            source = self

        self.auras.pop((aura, source), None)

    def has_aura(self, aura, source=None):
        if source is None:
            source = self

        if (aura, source) in self.auras:
            return True
        else:
            return False

    # Returns 0 if aura does not exist.
    def aura_duration(self, aura, source=None):
        if source is None:
            source = self

        if (aura, source) in self.auras:
            return self.auras[(aura, source)].duration
        else:
            return 0

    # Currently assumes the actor has access to the skill.
    def cooldown_duration(self, skill):
        if skill in self.cooldowns:
            return self.cooldowns[skill]
        else:
            return 0

    # Adds damage in terms of potency.
    def add_potency(self, potency):
        self.potency += potency

    def add_tp(self, value):
        if value >= 0:
            self.tp = min(self.tp + value, 1000)
        else:
            self.tp = max(self.tp + value, 0)

    def set_cooldown(self, skill, time):
        if time <= 0:
            self.check_now = True

        if skill in self.cooldowns:
            self.cooldowns[skill] = time

    def remove_cooldown(self, skill):
        self.cooldowns.pop(skill)

    # Gets the amount of time that needs to pass until something important happens.
    def get_time_of_interest(self):
        if self.check_now:
            self.check_now = False
            return 0

        times = [sys.maxint, self.gcd_timer, self.aa_timer, self.animation_lock] \
              + [aura.duration for aura in self.auras.values()] \
              + self.cooldowns.values()
        times = [time for time in times if time > 0]
        return min(times)

    def advance_cooldowns(self, time):
        cooldowns_to_remove = []
        for cooldown in self.cooldowns.keys():
            self.cooldowns[cooldown] = self.cooldowns[cooldown] - time
            if self.cooldowns[cooldown] <= 0:
                cooldowns_to_remove.append(cooldown)

        for cooldown_to_remove in cooldowns_to_remove:
            self.remove_cooldown(cooldown_to_remove)

    def advance_auras(self, time):
        auras_to_remove = []
        for aura_tuple, aura_timer in self.auras.iteritems():
            aura_timer.duration -= time
            if aura_timer.duration <= 0:
                auras_to_remove.append((aura_tuple[0], aura_tuple[1]))

        for aura_to_remove in auras_to_remove:
            self.remove_aura(aura_to_remove[0], aura_to_remove[1])

    # Advances time.
    def advance_time(self, time):
        self.gcd_timer -= time
        self.aa_timer -= time
        self.animation_lock -= time
        self.advance_auras(time)
        self.advance_cooldowns(time)

    # Includes DoT ticks and TP ticks
    def tick(self):
        self.add_tp(60)
        for aura_tuple in self.auras.keys():
            aura_tuple[0].tick(aura_tuple[1], self)

    def use(self, skill, target=None):
        if target is None:
            target = self

        if self.can_use(skill):
            skill.use(self, target)
            if skill == AutoAttack:
                self.aa_timer = self.aa_cooldown
            elif skill.is_off_gcd:
                self.animation_lock = skill.animation_lock
                self.cooldowns[skill] = skill.cooldown
            else:
                self.add_tp(-1 * skill.tp_cost)
                self.animation_lock = skill.animation_lock
                self.gcd_timer = self.gcd_cooldown

    # Currently assumes the actor has access to the skill.
    def can_use(self, skill):
        if skill == AutoAttack:
            return self.aa_ready()

        if self.animation_lock <= 0:
            if skill.is_off_gcd:
                return not skill in self.cooldowns
            else:
                return self.gcd_ready() and self.tp >= skill.tp_cost

    def gcd_ready(self):
        return self.gcd_timer <= 0

    def aa_ready(self):
        return self.aa_timer <= 0
