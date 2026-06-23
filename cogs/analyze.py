import os
import re

from discord.ext import commands

from parser.log_reader import read_log
from parser.encounter_parser import split_encounters
from parser.player_parser import parse_players
from utils.file_handler import prepare_uploaded_log, cleanup_old_uploads

from analyzers.dps import calculate_dps
from analyzers.healing import calculate_ehps
from analyzers.rotation import analyze_gcd_gaps
from analyzers.tank import analyze_tank_encounter

from services.operation_detector import detect_operation
from services.difficulty_detector import detect_difficulty
from services.role_detector import detect_role
from services.boss_detector import detect_boss_encounter
from discipline_analyzers.registry import analyze_discipline_specific

class CombinedEncounter:
    def __init__(self, boss_name, lines):
        self.boss_name = boss_name
        self.lines = lines

class Analyze(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.last_encounters = []
        self.players_data = {}

        self.player_dps_data = {}
        self.player_ehps_data = {}
        self.player_tank_data = {}

    # ---------------------------------------------------
    # Helpers
    # ---------------------------------------------------
    def get_lines(self, encounter):
        return encounter.lines if hasattr(encounter, "lines") else encounter

    def format_number(self, value):
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return str(value)

    def get_boss_name(self, encounter):
        if hasattr(encounter, "boss_name") and encounter.boss_name:
            return encounter.boss_name.strip()

        lines = self.get_lines(encounter)

        for line in lines:
            blocks = re.findall(r"\[(.*?)\]", line)

            if len(blocks) < 3:
                continue

            target = blocks[2]

            if "@" not in target and "{" in target:
                return target.split("{")[0].strip()

        return None

    def get_all_boss_names_from_dps(self):
        boss_names = set()

        for dps_by_boss in self.player_dps_data.values():
            for boss_name in dps_by_boss.keys():
                boss_names.add(boss_name)

        return sorted(boss_names)

    def find_boss_matches(self, boss_query):
        boss_query = boss_query.lower().strip()
        boss_names = self.get_all_boss_names_from_dps()

        exact_matches = [
            boss_name for boss_name in boss_names
            if boss_name.lower() == boss_query
        ]

        if exact_matches:
            return exact_matches

        partial_matches = [
            boss_name for boss_name in boss_names
            if boss_query in boss_name.lower()
        ]

        return partial_matches

    def find_player_name(self, player_query):
        player_query = player_query.lower().strip()

        all_players = (
            set(self.players_data.keys())
            | set(self.player_dps_data.keys())
            | set(self.player_ehps_data.keys())
            | set(self.player_tank_data.keys())
        )

        exact_matches = [
            player_name for player_name in all_players
            if player_name.lower() == player_query
        ]

        if exact_matches:
            return exact_matches[0]

        partial_matches = [
            player_name for player_name in all_players
            if player_query in player_name.lower()
        ]

        if len(partial_matches) == 1:
            return partial_matches[0]

        return None

    def get_player_role(self, player_name):
        player_info = self.players_data.get(player_name)

        if not player_info:
            return "UNKNOWN"

        return detect_role(
            player_info["class"],
            player_info["discipline"]
        )

    def parse_rotation_report(self, rotation_result):
        parsed = {
            "dots": [],
            "cooldowns": [],
            "core_abilities": [],
        }

        current_section = None

        for line in rotation_result.splitlines():
            line = line.strip()

            if "DoT / effect uptime" in line:
                current_section = "dots"
                continue

            if "Cooldown usage" in line:
                current_section = "cooldowns"
                continue

            if "Core ability usage" in line:
                current_section = "core_abilities"
                continue

            if not line.startswith("• "):
                continue

            clean_line = line.replace("• ", "", 1)

            if ":" not in clean_line:
                continue

            ability_name, value = clean_line.split(":", 1)

            ability_name = ability_name.strip()
            value = value.strip()

            if current_section == "dots" and "%" in value:
                percent_text = value.replace("%", "").strip()

                try:
                    parsed["dots"].append(
                        {
                            "ability": ability_name,
                            "uptime": float(percent_text),
                        }
                    )
                except ValueError:
                    pass

            elif current_section in ["cooldowns", "core_abilities"]:
                try:
                    parsed[current_section].append(
                        {
                            "ability": ability_name,
                            "uses": int(value),
                        }
                    )
                except ValueError:
                    pass

        return parsed

    async def send_long_message(self, ctx, message):
        max_length = 1900

        if len(message) <= max_length:
            await ctx.send(message)
            return

        chunks = []
        current_chunk = ""

        for line in message.split("\n"):
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk:
            chunks.append(current_chunk)

        for chunk in chunks:
            await ctx.send(chunk)

    # ---------------------------------------------------
    # !analyze
    # ---------------------------------------------------
    @commands.command()
    async def analyze(self, ctx):
        try:
            if not ctx.message.attachments:
                await ctx.send("Прикрепи TXT или ZIP файл.")
                return

            await ctx.send("⏳ Анализирую лог...")

            self.last_encounters = []
            self.players_data = {}

            self.player_dps_data = {}
            self.player_ehps_data = {}
            self.player_tank_data = {}

            cleanup_old_uploads(max_age_hours=24)

            attachment = ctx.message.attachments[0]

            log_path, upload_dir, debug_info = await prepare_uploaded_log(attachment)

            lines = read_log(log_path)
            encounters = split_encounters(lines)
            players_data = parse_players(lines)

            await ctx.send(
                "📥 Лог загружен\n"
                f"📦 Файл Discord: `{debug_info['uploaded_file']}`\n"
                f"📄 Читаю лог: `{debug_info['log_file']}`\n"
                f"📊 Строк в логе: `{len(lines)}`"
            )

            self.last_encounters = encounters
            self.players_data = players_data

            difficulty = None

            for encounter in encounters:
                difficulty = detect_difficulty(
                    self.get_lines(encounter)
                )
                break

            difficulty = None

            for encounter in encounters:
                difficulty = detect_difficulty(
                    self.get_lines(encounter)
                )
                break

            boss_lines_by_name = {}
            boss_detection_debug = {}

            for encounter in encounters:
                encounter_lines = self.get_lines(encounter)

                detection = detect_boss_encounter(encounter_lines)

                if not detection["is_boss_fight"]:
                    continue

                boss_name = detection["boss_name"]

                boss_lines_by_name.setdefault(
                    boss_name,
                    []
                )

                boss_lines_by_name[boss_name].extend(encounter_lines)

                boss_detection_debug.setdefault(
                    boss_name,
                    set()
                )

                boss_detection_debug[boss_name].add(
                    detection["matched_name"]
                )

            bosses = list(boss_lines_by_name.keys())

            combined_encounters = []

            for boss_name, boss_lines in boss_lines_by_name.items():
                combined_encounter = CombinedEncounter(
                    boss_name=boss_name,
                    lines=boss_lines
                )

                combined_encounters.append(combined_encounter)

                # DPS
                dps_data = calculate_dps(boss_lines)

                for player_name, dps in dps_data.items():
                    self.player_dps_data.setdefault(
                        player_name,
                        {}
                    )

                    self.player_dps_data[player_name][boss_name] = dps

                # HEAL / EHPS
                ehps_data = calculate_ehps(combined_encounter)

                for player_name, heal in ehps_data.items():
                    self.player_ehps_data.setdefault(
                        player_name,
                        {}
                    )

                    self.player_ehps_data[player_name][boss_name] = heal

                # TANK
                for player_name, player_info in players_data.items():
                    role = detect_role(
                        player_info["class"],
                        player_info["discipline"]
                    )

                    if role != "TANK":
                        continue

                    tank_data = analyze_tank_encounter(
                        combined_encounter,
                        player_name,
                        player_info["class"],
                        player_info["discipline"]
                    )

                    if not tank_data["has_data"]:
                        continue

                    self.player_tank_data.setdefault(
                        player_name,
                        {}
                    )

                    self.player_tank_data[player_name][boss_name] = tank_data

            self.last_encounters = combined_encounters

            operation_name = detect_operation(bosses)

            player_list = ""

            for name, info in players_data.items():
                role = detect_role(
                    info["class"],
                    info["discipline"]
                )

                player_list += (
                    f"• {name} — "
                    f"{info['class']} / "
                    f"{info['discipline']} "
                    f"({role})\n"
                )

            report = (
                    f"Операция: {operation_name}\n"
                    f"Сложность: {difficulty}\n\n"
                    f"Найдено боёв: {len(encounters)}\n\n"
                    f"**Боссы:**\n"
                    + ("\n".join(bosses) if bosses else "Не найдены")
                    + "\n\n"
                      f"**Игроки:**\n"
                    + (player_list if player_list else "Игроки не найдены")
                    + "\n"
                      f"Файл сохранён: {debug_info['uploaded_file']}\n"
                      f"Файл анализа: {debug_info['log_file']}\n"
                      f"Строк в логе: {len(lines)}\n\n"
                      f"Данные готовы для команд:\n"
                      f"`!player`, `!healer`, `!tank`, `!raid`, `!top`, `!compare`, `!coach`"
            )

            await self.send_long_message(ctx, report)

        except Exception as e:
            print("ERROR IN ANALYZE:", e)
            await ctx.send("Ошибка во время анализа. Проверь терминал.")

    # ---------------------------------------------------
    # !player <ник>
    # ---------------------------------------------------
    @commands.command()
    async def player(self, ctx, *, player_name: str):

        if not self.player_dps_data:
            await ctx.send("Сначала используй !analyze.")
            return

        player_name = self.find_player_name(player_name)

        if not player_name or player_name not in self.player_dps_data:
            await ctx.send("Игрок не найден или нет DPS-данных.")
            return

        response = f"**{player_name} — DPS по боссам:**\n\n"

        for boss, dps in self.player_dps_data[player_name].items():
            response += (
                f"• {boss}: "
                f"{self.format_number(dps)}\n"
            )

        await self.send_long_message(ctx, response)

    # ---------------------------------------------------
    # !healer <ник>
    # ---------------------------------------------------
    @commands.command()
    async def healer(self, ctx, *, player_name: str):

        if not self.player_ehps_data:
            await ctx.send("Сначала используй !analyze.")
            return

        player_name = self.find_player_name(player_name)

        if not player_name or player_name not in self.player_ehps_data:
            await ctx.send("Игрок не найден или нет лечения.")
            return

        response = f"**{player_name} — Healing:**\n\n"

        for boss, heal in self.player_ehps_data[player_name].items():
            raw_hps = heal.get("raw_hps", 0)
            ehps = heal.get("ehps", 0)

            response += (
                f"**{boss}**\n"
                f"Raw HPS: {self.format_number(raw_hps)}\n"
                f"EHPS: {self.format_number(ehps)}\n\n"
            )

        await self.send_long_message(ctx, response)

    # ---------------------------------------------------
    # !tank <ник>
    # ---------------------------------------------------
    @commands.command()
    async def tank(self, ctx, *, player_name: str):
        try:
            print("TANK COMMAND CALLED:", player_name)

            if not self.players_data:
                await ctx.send("Сначала используй !analyze.")
                return

            player_name = self.find_player_name(player_name)

            if not player_name:
                await ctx.send("Игрок не найден.")
                return

            player_info = self.players_data.get(player_name)

            if not player_info:
                await ctx.send("Игрок не найден в данных лога.")
                return

            role = detect_role(
                player_info["class"],
                player_info["discipline"]
            )

            if role != "TANK":
                await ctx.send(
                    f"**{player_name}** — не танк.\n"
                    f"Класс: {player_info['class']}\n"
                    f"Спек: {player_info['discipline']}\n"
                    f"Роль: {role}"
                )
                return

            if player_name not in self.player_tank_data:
                await ctx.send(
                    f"По танку **{player_name}** нет tank-данных.\n"
                    f"Проверь, получал ли он урон в найденных боях."
                )
                return

            response = (
                f"**Tank report: {player_name}**\n"
                f"Класс: {player_info['class']}\n"
                f"Спек: {player_info['discipline']}\n"
                f"Роль: {role}\n\n"
            )

            for boss_name, data in self.player_tank_data[player_name].items():
                response += f"## {boss_name}\n"

                response += (
                    f"Длительность боя: {data['fight_duration']} сек\n"
                    f"Получено урона: {self.format_number(data['damage_taken'])}\n"
                    f"Absorb: {self.format_number(data['absorbed_total'])}\n"
                    f"Absorb mitigation: {data['absorb_percent']}%\n"
                    f"Получено hits: {data['hits_taken']}\n"
                    f"Shielded hits: {data['shielded_hits']} "
                    f"({data['shield_rate']}%)\n"
                    f"Avoided hits: {data['avoided_hits']} "
                    f"({data['avoid_rate']}%)\n\n"
                )

                response += "**Taunts:**\n"

                if data["taunts"]:
                    for ability, count in data["taunts"].items():
                        response += f"• {ability}: {count}\n"
                else:
                    response += "• Не найдены\n"

                response += "\n**Defensives:**\n"

                if data["defensives"]:
                    for ability, count in data["defensives"].items():
                        response += f"• {ability}: {count}\n"
                else:
                    response += "• Не найдены\n"

                response += "\n**Uptime защитных эффектов:**\n"

                if data["effect_uptimes"]:
                    for effect_name, uptime in data["effect_uptimes"].items():
                        response += (
                            f"• {effect_name}: "
                            f"{uptime['percent']}% "
                            f"({uptime['seconds']} сек)\n"
                        )
                else:
                    response += "• Нет данных\n"

                if data["recommendations"]:
                    response += "\n**Рекомендации:**\n"

                    for recommendation in data["recommendations"]:
                        response += f"• {recommendation}\n"

                response += "\n"

            await self.send_long_message(ctx, response)

        except Exception as e:
            print("ERROR IN TANK:", e)
            await ctx.send("Ошибка в tank. Проверь терминал.")

    # ---------------------------------------------------
    # ---------------------------------------------------
    # !raid [босс]
    # ---------------------------------------------------
    @commands.command()
    async def raid(self, ctx, *, boss_query: str = None):

        if not self.player_dps_data:
            await ctx.send("Сначала используй !analyze.")
            return

        boss_dps_values = {}

        for player_name, dps_by_boss in self.player_dps_data.items():
            role = self.get_player_role(player_name)

            if role != "DPS":
                continue

            for boss_name, dps in dps_by_boss.items():
                boss_dps_values.setdefault(
                    boss_name,
                    []
                )

                boss_dps_values[boss_name].append(
                    {
                        "player": player_name,
                        "dps": dps,
                    }
                )

        if not boss_dps_values:
            await ctx.send("Нет DPS-данных для рейда.")
            return

        if boss_query:
            matches = self.find_boss_matches(boss_query)

            if not matches:
                available_bosses = "\n".join(
                    self.get_all_boss_names_from_dps()
                )

                await ctx.send(
                    "Босс не найден.\n\n"
                    "**Доступные боссы:**\n"
                    f"{available_bosses}"
                )
                return

            if len(matches) > 1:
                await ctx.send(
                    "Нашлось несколько боссов. Уточни название:\n\n"
                    + "\n".join(matches)
                )
                return

            boss_name = matches[0]

            if boss_name not in boss_dps_values:
                await ctx.send("По этому боссу нет DPS-данных.")
                return

            values = boss_dps_values[boss_name]
            avg_dps = sum(item["dps"] for item in values) / len(values)
            total_dps = sum(item["dps"] for item in values)

            values.sort(
                key=lambda item: item["dps"],
                reverse=True
            )

            response = (
                f"**Raid DPS: {boss_name}**\n"
                f"_Учитываются только DPS-роли._\n\n"
                f"Средний DPS: {self.format_number(avg_dps)}\n"
                f"Суммарный DPS: {self.format_number(total_dps)}\n"
                f"Игроков учтено: {len(values)}\n\n"
                f"**Игроки:**\n"
            )

            for item in values:
                response += (
                    f"• {item['player']}: "
                    f"{self.format_number(item['dps'])}\n"
                )

            await self.send_long_message(ctx, response)
            return

        response = "**Средний DPS рейда по боссам**\n"
        response += "_Учитываются только DPS-роли._\n\n"

        for boss_name, values in boss_dps_values.items():
            avg_dps = sum(item["dps"] for item in values) / len(values)
            total_dps = sum(item["dps"] for item in values)

            response += (
                f"**{boss_name}**\n"
                f"Средний DPS: {self.format_number(avg_dps)}\n"
                f"Суммарный DPS: {self.format_number(total_dps)}\n"
                f"Игроков учтено: {len(values)}\n\n"
            )

        await self.send_long_message(ctx, response)

    # ---------------------------------------------------
    # !top <босс>
    # ---------------------------------------------------
    @commands.command()
    async def top(self, ctx, *, boss_query: str):

        if not self.player_dps_data:
            await ctx.send("Сначала используй !analyze.")
            return

        matches = self.find_boss_matches(boss_query)

        if not matches:
            available_bosses = "\n".join(
                self.get_all_boss_names_from_dps()
            )

            await ctx.send(
                "Босс не найден.\n\n"
                "**Доступные боссы:**\n"
                f"{available_bosses}"
            )
            return

        if len(matches) > 1:
            boss_list = "\n".join(matches)

            await ctx.send(
                "Нашлось несколько боссов. Уточни название:\n\n"
                f"{boss_list}"
            )
            return

        boss_name = matches[0]
        ranking = []

        for player_name, dps_by_boss in self.player_dps_data.items():

            if boss_name not in dps_by_boss:
                continue

            ranking.append(
                {
                    "player": player_name,
                    "dps": dps_by_boss[boss_name],
                    "role": self.get_player_role(player_name),
                }
            )

        if not ranking:
            await ctx.send("По этому боссу нет DPS-данных.")
            return

        ranking.sort(
            key=lambda item: item["dps"],
            reverse=True
        )

        response = f"**Топ DPS: {boss_name}**\n\n"

        for index, item in enumerate(ranking, start=1):
            response += (
                f"{index}. {item['player']} "
                f"({item['role']}) — "
                f"{self.format_number(item['dps'])}\n"
            )

        await self.send_long_message(ctx, response)

    # ---------------------------------------------------
    # !compare Игрок 1 | Игрок 2
    # ---------------------------------------------------
    @commands.command()
    async def compare(self, ctx, *, players: str):

        if not self.player_dps_data:
            await ctx.send("Сначала используй !analyze.")
            return

        if "|" not in players:
            await ctx.send(
                "Используй формат:\n"
                "`!compare Игрок 1 | Игрок 2`\n\n"
                "Пример:\n"
                "`!compare Allaria Nargin | Doomdrain`"
            )
            return

        raw_player_1, raw_player_2 = players.split("|", 1)

        player_1 = self.find_player_name(raw_player_1)
        player_2 = self.find_player_name(raw_player_2)

        if not player_1:
            await ctx.send(
                f"Первый игрок не найден: `{raw_player_1.strip()}`"
            )
            return

        if not player_2:
            await ctx.send(
                f"Второй игрок не найден: `{raw_player_2.strip()}`"
            )
            return

        if player_1 not in self.player_dps_data:
            await ctx.send(f"У игрока {player_1} нет DPS-данных.")
            return

        if player_2 not in self.player_dps_data:
            await ctx.send(f"У игрока {player_2} нет DPS-данных.")
            return

        player_1_data = self.player_dps_data[player_1]
        player_2_data = self.player_dps_data[player_2]

        common_bosses = (
            set(player_1_data.keys())
            & set(player_2_data.keys())
        )

        if not common_bosses:
            await ctx.send("У игроков нет общих боссов для сравнения.")
            return

        response = (
            f"**Сравнение DPS**\n"
            f"{player_1} vs {player_2}\n\n"
        )

        player_1_wins = 0
        player_2_wins = 0
        draws = 0

        for boss_name in sorted(common_bosses):
            dps_1 = player_1_data[boss_name]
            dps_2 = player_2_data[boss_name]

            difference = abs(dps_1 - dps_2)

            if dps_1 > dps_2:
                winner = player_1
                player_1_wins += 1
            elif dps_2 > dps_1:
                winner = player_2
                player_2_wins += 1
            else:
                winner = "ничья"
                draws += 1

            response += (
                f"**{boss_name}**\n"
                f"{player_1}: {self.format_number(dps_1)}\n"
                f"{player_2}: {self.format_number(dps_2)}\n"
                f"Сильнее: {winner}\n"
                f"Разница: {self.format_number(difference)} DPS\n\n"
            )

        response += "**Итог:**\n"
        response += f"{player_1}: побед по боссам — {player_1_wins}\n"
        response += f"{player_2}: побед по боссам — {player_2_wins}\n"

        if draws:
            response += f"Ничьих: {draws}\n"

        if player_1_wins > player_2_wins:
            response += f"\nОбщий победитель: **{player_1}**"
        elif player_2_wins > player_1_wins:
            response += f"\nОбщий победитель: **{player_2}**"
        else:
            response += "\nОбщий результат: **примерно равно**"

        await self.send_long_message(ctx, response)

    # ---------------------------------------------------
    # !coach <ник>
    # DPS coach по всем боссам
    # ---------------------------------------------------
    @commands.command()
    async def coach(self, ctx, *, player_name: str):
        try:
            if not self.players_data:
                await ctx.send("Сначала используй !analyze.")
                return

            player_name = self.find_player_name(player_name)

            if not player_name or player_name not in self.players_data:
                await ctx.send("Игрок не найден в загруженном логе.")
                return

            player_info = self.players_data[player_name]

            player_class = player_info["class"]
            discipline = player_info["discipline"]

            role = detect_role(
                player_class,
                discipline
            )

            if role == "HEAL":
                await ctx.send(
                    f"**{player_name}** — {player_class} / {discipline}\n"
                    f"Роль: HEAL\n\n"
                    f"Для хилеров используй отдельную команду:\n"
                    f"`!healer {player_name}`\n\n"
                    f"`!coach` сейчас предназначен для DPS-анализа."
                )
                return

            if role == "TANK":
                await ctx.send(
                    f"**{player_name}** — {player_class} / {discipline}\n"
                    f"Роль: TANK\n\n"
                    f"Для танков используй отдельную команду:\n"
                    f"`!tank {player_name}`\n\n"
                    f"`!coach` сейчас предназначен для DPS-анализа."
                )
                return

            if role != "DPS":
                await ctx.send(
                    f"**{player_name}** — {player_class} / {discipline}\n"
                    f"Роль не определена."
                )
                return

            if not self.last_encounters:
                await ctx.send("Нет данных для анализа.")
                return

            response = (
                f"**Coach report: {player_name}**\n"
                f"Класс: {player_class}\n"
                f"Спек: {discipline}\n"
                f"Роль: {role}\n\n"
            )

            analyzed_any_boss = False

            from services.rotation_engine import analyze_rotation

            for encounter in self.last_encounters:
                encounter_lines = self.get_lines(encounter)
                boss_name = self.get_boss_name(encounter) or "Unknown boss"

                player_was_active = False

                for line in encounter_lines:
                    if (
                            f"@{player_name}#" in line
                            and "AbilityActivate" in line
                    ):
                        player_was_active = True
                        break

                if not player_was_active:
                    continue

                result = analyze_gcd_gaps(
                    encounter_lines,
                    player_name
                )

                if not result:
                    continue

                analyzed_any_boss = True

                rotation_result = analyze_rotation(
                    player_name,
                    encounter_lines,
                    player_class,
                    discipline
                )

                if not rotation_result:
                    rotation_result = ""

                score = 100
                recommendations = []

                # ---------------- GCD / downtime score ----------------
                if result["avg_gap"] > 1.7:
                    score -= 10
                    recommendations.append(
                        "Сократи средние простои между способностями."
                    )

                if result["long_gaps_count"] > 25:
                    score -= 20
                    recommendations.append(
                        f"Обнаружено {result['long_gaps_count']} длинных простоев. "
                        f"Это сильно режет DPS."
                    )

                elif result["long_gaps_count"] > 15:
                    score -= 10
                    recommendations.append(
                        f"Обнаружено {result['long_gaps_count']} длинных простоев. "
                        f"Проверь движение, позиционирование и приоритет способностей."
                    )

                if result["max_gap"] > 6:
                    score -= 10
                    recommendations.append(
                        f"Максимальный простой {result['max_gap']} сек. "
                        f"Это слишком много для DPS-ротации."
                    )

                parsed_rotation = self.parse_rotation_report(
                    rotation_result
                )

                # ---------------- DoT uptime score ----------------
                for dot_info in parsed_rotation["dots"]:
                    ability_name = dot_info["ability"]
                    uptime = dot_info["uptime"]

                    if uptime < 70:
                        score -= 20
                        recommendations.append(
                            f"{ability_name} держится только {uptime}%. "
                            f"Это критически низкий uptime."
                        )

                    elif uptime < 85:
                        score -= 15
                        recommendations.append(
                            f"{ability_name} держится только {uptime}%. "
                            f"Нужно заметно чаще обновлять эффект."
                        )

                    elif uptime < 95:
                        score -= 5
                        recommendations.append(
                            f"{ability_name} uptime {uptime}%. "
                            f"Можно улучшить до 95%+."
                        )

                # ---------------- Cooldown usage score ----------------
                for cd_info in parsed_rotation["cooldowns"]:
                    ability_name = cd_info["ability"]
                    uses = cd_info["uses"]

                    if uses == 0:
                        score -= 10
                        recommendations.append(
                            f"{ability_name} не использован в бою."
                        )

                # ---------------- Core abilities score ----------------
                for core_info in parsed_rotation["core_abilities"]:
                    ability_name = core_info["ability"]
                    uses = core_info["uses"]

                    if uses == 0:
                        score -= 10
                        recommendations.append(
                            f"{ability_name} не найден в бою."
                        )

                score = max(
                    0,
                    min(score, 98)
                )

                response += (
                    f"## {boss_name}\n\n"
                    f"**GCD / downtime:**\n"
                    f"Средний GCD gap: {result['avg_gap']} сек\n"
                    f"Максимальный простой: {result['max_gap']} сек\n"
                    f"Длинных простоев (>2 сек): {result['long_gaps_count']}\n"
                )

                response += rotation_result

                discipline_result = analyze_discipline_specific(
                    player_name,
                    encounter_lines,
                    player_class,
                    discipline
                )

                if discipline_result:
                    response += discipline_result

                response += f"\nPerformance Score: {score}/100\n"

                if recommendations:
                    response += "\n**Рекомендации:**\n"

                    for recommendation in recommendations:
                        response += f"• {recommendation}\n"

                response += "\n"

            if not analyzed_any_boss:
                await ctx.send(
                    "Не нашла бои, где игрок активно использовал способности."
                )
                return

            await self.send_long_message(ctx, response)

        except Exception as e:
            print("ERROR IN COACH:", e)
            await ctx.send("Ошибка в coach. Проверь терминал.")


async def setup(bot):
    await bot.add_cog(Analyze(bot))