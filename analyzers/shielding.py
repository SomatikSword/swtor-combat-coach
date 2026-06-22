import re
from collections import defaultdict


def calculate_shield_absorb(encounter):

    lines = encounter.lines

    active_shields = {}   # target -> caster
    shield_absorb = defaultdict(float)

    for line in lines:

        # ✅ Shield applied
        if "Protected" in line:

            blocks = re.findall(r"\[(.*?)\]", line)
            if len(blocks) >= 3:

                source_block = blocks[1]
                target_block = blocks[2]

                if source_block.startswith("@"):
                    caster = source_block.split("#")[0][1:]
                    target = target_block.split("{")[0]

                    active_shields[target] = caster

        # ✅ Shield removed
        if "RemoveEffect" in line and "Protected" in line:

            blocks = re.findall(r"\[(.*?)\]", line)
            if len(blocks) >= 3:
                target_block = blocks[2]
                target = target_block.split("{")[0]

                if target in active_shields:
                    del active_shields[target]

        # ✅ Damage event
        if "Damage" in line:

            raw_match = re.search(r'\(([\d\.]+)', line)
            final_match = re.search(r'<([\d\.]+)>', line)

            if raw_match and final_match:

                raw_damage = float(raw_match.group(1))
                final_damage = float(final_match.group(1))

                if raw_damage > final_damage:

                    absorbed = raw_damage - final_damage

                    blocks = re.findall(r"\[(.*?)\]", line)
                    if len(blocks) >= 3:

                        target_block = blocks[2]
                        target = target_block.split("{")[0]

                        # ✅ считаем absorb только если shield активен
                        if target in active_shields:
                            caster = active_shields[target]
                            shield_absorb[caster] += absorbed

    return shield_absorb