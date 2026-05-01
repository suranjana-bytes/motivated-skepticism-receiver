import itertools
import random
import sqlite3
import time
from functools import lru_cache
from pathlib import Path

from otree.api import *


doc = """
Receiver-only experiment with instructions, an IQ section, 10 decision rounds,
and final demographics.
"""


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SENDER_DB_PATH = BASE_DIR.parent / "Thesis Experiment" / "db.sqlite3"
RAVEN_PARTICIPANT_PERFORMANCE_DATA = [
    dict(sender_id=1, items=99, correct=90),
    dict(sender_id=2, items=99, correct=90),
    dict(sender_id=3, items=99, correct=86),
    dict(sender_id=4, items=100, correct=89),
    dict(sender_id=5, items=97, correct=81),
    dict(sender_id=6, items=96, correct=77),
    dict(sender_id=7, items=94, correct=73),
    dict(sender_id=8, items=101, correct=63),
    dict(sender_id=9, items=99, correct=67),
    dict(sender_id=10, items=98, correct=42),
    dict(sender_id=11, items=100, correct=45),
    dict(sender_id=12, items=97, correct=22),
    dict(sender_id=13, items=101, correct=61),
    dict(sender_id=14, items=100, correct=49),
    dict(sender_id=15, items=100, correct=37),
]
SENDER_DECISION_DATA = [
    dict(sender_id=1, status="Low Status", rounds=[dict(type_number=2, message="{1, 2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=2, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=2, message="{1, 2}")]),
    dict(sender_id=3, status="Low Status", rounds=[dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}")]),
    dict(sender_id=4, status="Low Status", rounds=[dict(type_number=1, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}")]),
    dict(sender_id=6, status="Low Status", rounds=[dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{3}"), dict(type_number=1, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{2}"), dict(type_number=3, message="{3}"), dict(type_number=1, message="{1}")]),
    dict(sender_id=7, status="Low Status", rounds=[dict(type_number=3, message="{3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1, 2}"), dict(type_number=3, message="{3}"), dict(type_number=3, message="{3}"), dict(type_number=3, message="{3}"), dict(type_number=1, message="{1}")]),
    dict(sender_id=9, status="Low Status", rounds=[dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2, 3}")]),
    dict(sender_id=11, status="High Status", rounds=[dict(type_number=1, message="{1}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2, 3}")]),
    dict(sender_id=13, status="High Status", rounds=[dict(type_number=1, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}")]),
    dict(sender_id=14, status="High Status", rounds=[dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1, 2}"), dict(type_number=3, message="{2, 3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=2, message="{1, 2, 3}")]),
    dict(sender_id=15, status="High Status", rounds=[dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=3, message="{2, 3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{2, 3}")]),
    dict(sender_id=16, status="High Status", rounds=[dict(type_number=1, message="{1}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1}")]),
    dict(sender_id=17, status="High Status", rounds=[dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1}"), dict(type_number=1, message="{1}")]),
    dict(sender_id=18, status="High Status", rounds=[dict(type_number=1, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=1, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=1, message="{1, 2, 3}"), dict(type_number=3, message="{1, 2, 3}"), dict(type_number=2, message="{1, 2}"), dict(type_number=2, message="{1, 2}"), dict(type_number=3, message="{1, 2, 3}")]),
]


class C(BaseConstants):
    NAME_IN_URL = "receiver_experiment"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    IQ_TIME_LIMIT_SECONDS = 10 * 60
    TOTAL_EXPERIMENT_SCREENS = 50
    NUMBER_CHOICES = [1, 2, 3]
    STATUS_CHOICES = ["High Status", "Low Status"]
    POINTS_FOR_CORRECT_GUESS = cu(1)
    IQ_OPTION_VALUES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
    AGE_CHOICES = list(range(18, 101))
    EDUCATION_LEVELS = [
        "High School diploma",
        "Bachelors Degree",
        "Master's Degree or Above",
    ]
    GENDER_OPTIONS = [
        "Male",
        "Female",
        "Other/prefer not to say",
    ]
    IQ_ITEMS = [
        dict(question_id="Q2", correct="R1"),
        dict(question_id="Q8", correct="R1"),
        dict(question_id="Q11", correct="R5"),
        dict(question_id="Q12", correct="R6"),
        dict(question_id="Q15", correct="R2"),
        dict(question_id="Q17", correct="R6"),
        dict(question_id="Q18", correct="R7"),
        dict(question_id="Q24", correct="R3"),
        dict(question_id="Q26", correct="R2"),
        dict(question_id="Q30", correct="R5"),
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    sender_number = models.IntegerField()
    sender_status = models.StringField()
    sender_message = models.StringField()
    guess = models.IntegerField(
        choices=C.NUMBER_CHOICES,
        widget=widgets.RadioSelect,
        label="",
    )
    iq_answer_1 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_2 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_3 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_4 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_5 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_6 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_7 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_8 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_9 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    iq_answer_10 = models.StringField(choices=C.IQ_OPTION_VALUES, blank=True)
    age = models.IntegerField(
        choices=C.AGE_CHOICES,
        blank=True,
        label="1. What is your age?",
    )
    gender = models.StringField(
        choices=C.GENDER_OPTIONS,
        widget=widgets.RadioSelect,
        blank=True,
        label="2. What is your gender?",
    )
    education_level = models.StringField(
        choices=C.EDUCATION_LEVELS,
        widget=widgets.RadioSelect,
        blank=True,
        label="3. What is your highest level of education?",
    )


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        assign_sender_round_data(player)


def build_sender_message(true_number: int) -> str:
    valid_messages = []
    for subset_size in range(1, len(C.NUMBER_CHOICES) + 1):
        for subset in itertools.combinations(C.NUMBER_CHOICES, subset_size):
            if true_number in subset:
                valid_messages.append(subset)

    message_numbers = random.choice(valid_messages)
    return "{" + ",".join(str(number) for number in message_numbers) + "}"


def sender_message_numbers(sender_message: str):
    inner = sender_message.strip("{}")
    return [int(part.strip()) for part in inner.split(",") if part.strip()]


def receiver_message_display(sender_message: str) -> str:
    numbers = sender_message_numbers(sender_message)
    if len(numbers) == 1:
        number_text = str(numbers[0])
    else:
        number_text = ", ".join(str(number) for number in numbers[:-1])
        number_text = f"{number_text} or {numbers[-1]}"
    return f"It is {number_text}"


@lru_cache(maxsize=1)
def load_sender_decisions():
    if not DEFAULT_SENDER_DB_PATH.exists():
        return {}

    query = """
        SELECT participant_id, round_number, sender_status, type_number, sent_message
        FROM sender_experiment_player
        WHERE participant_id IS NOT NULL
          AND round_number IS NOT NULL
          AND sender_status IS NOT NULL
          AND type_number IS NOT NULL
          AND sent_message IS NOT NULL
        ORDER BY participant_id, round_number
    """

    try:
        with sqlite3.connect(DEFAULT_SENDER_DB_PATH) as connection:
            rows = connection.execute(query).fetchall()
    except sqlite3.Error:
        return {}

    decisions_by_participant = {}
    for participant_id, round_number, sender_status, type_number, sent_message in rows:
        decisions_by_participant.setdefault(participant_id, {})[round_number] = dict(
            sender_status=sender_status,
            sender_number=type_number,
            sender_message=sent_message,
        )
    return decisions_by_participant


def imported_sender_ids():
    complete_ids = []
    for participant_id, rounds in load_sender_decisions().items():
        if all(round_number in rounds for round_number in range(1, C.NUM_ROUNDS + 1)):
            complete_ids.append(participant_id)
    return complete_ids


def assigned_imported_sender_id(player: Player):
    sender_ids = imported_sender_ids()
    if not sender_ids:
        return None
    index = (player.participant.id_in_session - 1) % len(sender_ids)
    return sender_ids[index]


def imported_sender_round(player: Player):
    sender_participant_id = assigned_imported_sender_id(player)
    if sender_participant_id is None:
        return None
    return load_sender_decisions().get(sender_participant_id, {}).get(player.round_number)


def assign_sender_round_data(player: Player):
    imported_round = imported_sender_round(player)
    if imported_round:
        player.sender_number = imported_round["sender_number"]
        player.sender_status = imported_round["sender_status"]
        player.sender_message = imported_round["sender_message"]
        return

    sender_number = random.choice(C.NUMBER_CHOICES)
    player.sender_number = sender_number
    player.sender_status = random.choice(C.STATUS_CHOICES)
    player.sender_message = build_sender_message(sender_number)


def instruction_progress(screen_number: int) -> dict:
    total = 2
    return dict(
        phase_label="",
        screen_counter=f"Screen {screen_number} of {total}",
        progress_percent=(screen_number / C.TOTAL_EXPERIMENT_SCREENS) * 100,
    )


def round_progress(player: Player, screen_number: int) -> dict:
    total = 3
    completed = 17 + ((player.round_number - 1) * total) + screen_number
    return dict(
        phase_label="",
        screen_counter=(
            f"Round {player.round_number} of {C.NUM_ROUNDS} "
            f"- Screen {screen_number} of {total}"
        ),
        progress_percent=(completed / C.TOTAL_EXPERIMENT_SCREENS) * 100,
    )


def iq_progress(screen_number: int) -> dict:
    total = len(C.IQ_ITEMS)
    return dict(
        phase_label="",
        screen_counter=f"Matrix {screen_number} of {total}",
        progress_percent=((3 + screen_number) / C.TOTAL_EXPERIMENT_SCREENS) * 100,
    )


def info_context(**kwargs) -> dict:
    defaults = dict(
        round_chip="",
        bullets=[],
        secondary_bullets=[],
        instruction_lines=[],
        heading_class="",
        status_badge_class="",
        status_badge="",
        message_box="",
        footer="",
    )
    defaults.update(kwargs)
    return defaults


def iq_item(item_number: int) -> dict:
    item = C.IQ_ITEMS[item_number - 1].copy()
    question_id = item["question_id"]
    item["item_number"] = item_number
    item["stem_path"] = f"receiver_experiment/raven/{question_id}/stem.png"
    item["prompt"] = "Select the option that best completes the matrix."
    item["options"] = [
        dict(
            value=option_value,
            label=str(index),
            image_path=f"receiver_experiment/raven/{question_id}/{option_value}.png",
        )
        for index, option_value in enumerate(C.IQ_OPTION_VALUES, start=1)
    ]
    return item


def iq_score(player: Player) -> int:
    round_one = player.in_round(1)
    answers = [
        round_one.field_maybe_none(f"iq_answer_{item_number}")
        for item_number in range(1, len(C.IQ_ITEMS) + 1)
    ]
    return sum(
        1 for answer, item in zip(answers, C.IQ_ITEMS) if answer == item["correct"]
    )


def performance_rate(record: dict) -> float:
    return record["correct"] / record["items"]


def receiver_iq_rank(
    receiver_rate: float, first_comparison_rate: float, second_comparison_rate: float
) -> int:
    ranking = [
        ("receiver", receiver_rate),
        ("first_comparison", first_comparison_rate),
        ("second_comparison", second_comparison_rate),
    ]
    random.shuffle(ranking)
    ranking.sort(key=lambda item: item[1], reverse=True)
    return next(index for index, item in enumerate(ranking, start=1) if item[0] == "receiver")


def sender_choice_for_rank(
    round_number: int, iq_rank: int, used_sender_ids: set, status_counts: dict
):
    matching_choices = []
    unused_matching_choices = []
    for sender in SENDER_DECISION_DATA:
        round_decision = sender["rounds"][round_number - 1]
        if round_decision["type_number"] != iq_rank:
            continue
        choice = (sender, round_decision)
        matching_choices.append(choice)
        if sender["sender_id"] not in used_sender_ids:
            unused_matching_choices.append(choice)

    choice_pool = unused_matching_choices or matching_choices
    if not choice_pool:
        return None, None

    status_preference = C.STATUS_CHOICES.copy()
    random.shuffle(status_preference)
    status_preference.sort(key=lambda status: status_counts.get(status, 0))
    for status in status_preference:
        status_choices = [
            choice for choice in choice_pool if choice[0]["status"] == status
        ]
        if status_choices:
            return random.choice(status_choices)

    return random.choice(choice_pool)


def assign_receiver_iq_rank_rounds(player: Player):
    if player.participant.vars.get("receiver_iq_rank_rounds_assigned"):
        return

    if len(RAVEN_PARTICIPANT_PERFORMANCE_DATA) < 2:
        for round_player in player.in_all_rounds():
            assign_sender_round_data(round_player)
        player.participant.vars["receiver_iq_rank_rounds_assigned"] = True
        return

    receiver_rate = iq_score(player) / len(C.IQ_ITEMS)
    raven_pairs = list(itertools.combinations(RAVEN_PARTICIPANT_PERFORMANCE_DATA, 2))
    if len(raven_pairs) >= C.NUM_ROUNDS:
        selected_raven_pairs = random.sample(raven_pairs, C.NUM_ROUNDS)
    else:
        selected_raven_pairs = [
            random.sample(RAVEN_PARTICIPANT_PERFORMANCE_DATA, 2)
            for _ in range(C.NUM_ROUNDS)
    ]
    round_assignments = []
    used_sender_ids = set()
    status_counts = {status: 0 for status in C.STATUS_CHOICES}

    for round_player, raven_pair in zip(player.in_all_rounds(), selected_raven_pairs):
        first_comparison, second_comparison = list(raven_pair)
        iq_rank = receiver_iq_rank(
            receiver_rate,
            performance_rate(first_comparison),
            performance_rate(second_comparison),
        )
        sender_record, sender_round_decision = sender_choice_for_rank(
            round_player.round_number, iq_rank, used_sender_ids, status_counts
        )

        round_player.sender_number = iq_rank
        if sender_record and sender_round_decision:
            round_player.sender_status = sender_record["status"]
            round_player.sender_message = sender_round_decision["message"]
            used_sender_ids.add(sender_record["sender_id"])
        else:
            round_player.sender_status = min(
                C.STATUS_CHOICES, key=lambda status: status_counts.get(status, 0)
            )
            round_player.sender_message = build_sender_message(iq_rank)
        status_counts[round_player.sender_status] += 1

        round_assignments.append(
            dict(
                round_number=round_player.round_number,
                first_raven_participant_id=first_comparison["sender_id"],
                second_raven_participant_id=second_comparison["sender_id"],
                sender_id=sender_record["sender_id"] if sender_record else None,
                sender_status=round_player.sender_status,
                sender_type_number=(
                    sender_round_decision["type_number"] if sender_round_decision else None
                ),
                receiver_iq_rank=iq_rank,
            )
        )

    player.participant.vars["receiver_iq_rank_round_assignments"] = round_assignments
    player.participant.vars["receiver_iq_rank_rounds_assigned"] = True


class StaticInfoPage(Page):
    template_name = "receiver_experiment/InfoPage.html"


class Welcome(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            eyebrow="",
            heading="Welcome to The Study!",
            paragraphs=[],
            button_label="Next",
            **instruction_progress(1),
        )


class ParticipationInformation(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            eyebrow="",
            heading="Information",
            paragraphs=[
                "Before starting the experiment, please read the following information carefully.",
                (
                    "Your participation in this study is voluntary. You are free "
                    "to stop the study at any time, without providing a reason and "
                    "without any negative consequences."
                ),
                (
                    "Please note that you will not receive any real monetary "
                    "payment for participating in this study. The payments "
                    "mentioned are hypothetical and are used the study. But "
                    "please act as if they are real."
                ),
                (
                    "All the data collected are anonymous and for research "
                    "purposes only. If you have any question during the "
                    "experiment, please send it to suranjana.ac@gmail.com."
                ),
                "The experiment has 2 parts. It takes around 15 minutes to finish.",
                "Instructions are given along the way.",
                (
                    "By continuing, you confirm that you have read and understood "
                    "this information and agree to participate in the study."
                ),
            ],
            button_label="Next",
            **instruction_progress(2),
        )


class YourRole(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            eyebrow="",
            heading="Your Role",
            paragraphs=[
                "Today, you are a Receiver.",
                (
                    "Another participant that you will be randomly paired with, "
                    "called the Sender, will observe a number from 1, 2 or 3 and "
                    "send you a message containing one or more numbers."
                ),
                "Your task is to guess your IQ.",
            ],
            button_label="Next",
            **instruction_progress(3),
        )


class IQIntro(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            phase_label="",
            screen_counter="Introduction",
            progress_percent=(3 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
            eyebrow="",
            heading="Part 1",
            paragraphs=[
                (
                    "Part 1 consists of a Raven IQ-test, a test frequently used "
                    "to measure intelligence. It measures the ability to reason "
                    "clearly and grasp complexity. Performance in the test is "
                    "often associated with educational success and high future income."
                ),
                (
                    "The test has 10 questions. For every question, you will see "
                    "a pattern with a missing piece."
                ),
                (
                    "Your task is to complete the pattern by choosing one of the "
                    "pieces that are proposed to you."
                ),
                "You will have 10 minutes to answer all the questions.",
                (
                    "Payoff: you will earn 0.50 cents for each correct answer. "
                    "In this part, you can earn up to 5 euros (15 ∗ 0.50)."
                ),
            ],
            button_label="Start IQ Test",
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars["iq_deadline"] = time.time() + C.IQ_TIME_LIMIT_SECONDS


def iq_seconds_remaining(player: Player) -> int:
    deadline = player.participant.vars.get("iq_deadline")
    if not deadline:
        return C.IQ_TIME_LIMIT_SECONDS
    return max(0, int(deadline - time.time()))


class IQQuestion(Page):
    template_name = "receiver_experiment/IQPage.html"
    form_model = "player"
    item_number = 1

    @classmethod
    def is_displayed(cls, player: Player):
        return player.round_number == 1 and iq_seconds_remaining(player) > 0

    @classmethod
    def get_form_fields(cls, player: Player):
        return [f"iq_answer_{cls.item_number}"]

    @classmethod
    def get_timeout_seconds(cls, player: Player):
        return iq_seconds_remaining(player)

    @classmethod
    def vars_for_template(cls, player: Player):
        return dict(
            form_field_name=f"iq_answer_{cls.item_number}",
            item=iq_item(cls.item_number),
            remaining_seconds=iq_seconds_remaining(player),
            **iq_progress(cls.item_number),
        )


class IQQuestion1(IQQuestion):
    item_number = 1


class IQQuestion2(IQQuestion):
    item_number = 2


class IQQuestion3(IQQuestion):
    item_number = 3


class IQQuestion4(IQQuestion):
    item_number = 4


class IQQuestion5(IQQuestion):
    item_number = 5


class IQQuestion6(IQQuestion):
    item_number = 6


class IQQuestion7(IQQuestion):
    item_number = 7


class IQQuestion8(IQQuestion):
    item_number = 8


class IQQuestion9(IQQuestion):
    item_number = 9


class IQQuestion10(IQQuestion):
    item_number = 10


class IQEnd(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            phase_label="",
            screen_counter="Part 1 Complete",
            progress_percent=(14 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
            eyebrow="",
            heading="Part 1 has now ended",
            paragraphs=["Part 2 will begin."],
            button_label="Next",
        )


class Part2Intro(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            phase_label="",
            screen_counter="Part 2",
            progress_percent=(15 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
            eyebrow="",
            heading="Part 2",
            paragraphs=[],
            instruction_lines=[
                dict(text="Part 2 consists of 10 rounds of a 2-player game. A sender and a reciever.", css_class=""),
                dict(text="Today you are a Reciever!", css_class="emphasis-line"),
                dict(text="You will be randomly matched with a sender, you will never know the identity of the other player and this player can be new in each round.", css_class=""),
            ],
            button_label="Next",
        )


class IQTransition(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            phase_label="",
            screen_counter="Instructions",
            progress_percent=(16 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
            eyebrow="",
            heading="Instructions",
            paragraphs=[],
            bullets=[],
            secondary_bullets=[],
            instruction_lines=[
                dict(text="Description of the game: Each round of the game has 5 steps.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="⋄ Step 1: The same IQ-test that you did earlier was also done by a large number of previous participants. In each round of the game, the computer randomly selects 2 previous participants. Together with these participants, you will form a group of 3 participants. Within this group, the computer program compares the performances in the IQ-test. It will then compute your IQ-rank for the round as follows:", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="⋄ If you have the highest performance in the group of 3, your IQ-rank will be 1.", css_class=""),
                dict(text="⋄ If you have the second highest perfance in the group of 3, your IQ-rank will be 2.", css_class=""),
                dict(text="⋄ If you have the lowest perfance in the group of 3, your IQ-rank will be 3.", css_class=""),
                dict(text="⋄ If you have the same performance as other participants in the group, the computer program randomly decides the ranking between these participants and yourself.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="In each round, your IQ-rank will be 1, 2 or 3. The higher your IQ-rank, the worse you performed in the IQ-test relative to the other participants.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="Note: In each round, the computer randomly selects new previous participants whose performance is compared to yours, so your IQ-rank can change across rounds.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="⋄ Step 2: The senders you will play with completed similar IQ test at the beginning of the study. Based on their performance, they are classified into two groups:", css_class=""),
                dict(text="* High-status senders: those in the top half of the sender population", css_class=""),
                dict(text="* Low-status senders: those in the bottom half of the sender population", css_class=""),
                dict(text="During the 10 rounds of the sender–receiver game, you will be matched with different senders. At the start of each round, you will be informed whether your sender is high-status or low-status.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="⋄ Step 3: The Sender is informed of a number, which is 1, 2 or 3. This number corresponds to your IQ-rank, but the Sender does not know that this is the case. For him/her, this number has no particular meaning. You are not informed of this IQ-rank, but your task is to guess it.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="⋄ Step 4: Before you guess your IQ-rank, the Sender gives you information about it. This information will take the form of a set of numbers, with the only constraint that your IQ-rank must be part of the set. Said differently, your IQ-rank is always one of the numbers sent by the Sender. For instance, if your IQ-rank is 2, then the Sender can send you any of the sets of numbers given in the table below:", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="Available sets of numbers", css_class=""),
                dict(text="□{1, 2, 3} ", css_class=""),
                dict(text="□{1, 2} ", css_class=""),
                dict(text="□{2, 3} ", css_class=""),
                dict(text="□{2} ", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="⋄ Step 5: The information given by the Sender will be displayed on your screen, and you will finally make your guess. Your guess can be any number between 1 and 3. Once you made your guess, the round is over and a new round starts.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="In each round, the payoffs are as follows. The Sender knows these payoffs too.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="Sender’s Payoff: The Sender’s payoff corresponds exactly to your guess in this round.", css_class=""),
                dict(text="Sender’s payoff = 4 − (your guess)", css_class="formula-line"),
                dict(text="", css_class="spacer-line"),
                dict(text="Simply put, the Sender earns more when you guess a lower number.", css_class="emphasis-line"),
                dict(text="", css_class="spacer-line"),
                dict(text="Your Payoff: Your payoff depends on how close is your guess to your IQ-rank.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="Your payoff = 3 − | your guess − your IQ-rank |", css_class="formula-line"),
                dict(text="", css_class="spacer-line"),
                dict(text="where | your guess − your IQ-rank | is the distance between your guess and your IQ-rank in the round.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="Simply put, you earn more when your guess is closer to your IQ-rank.", css_class="emphasis-line"),
            ],
            button_label="Next",
        )


class GameSummaryInstructions(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            phase_label="",
            screen_counter="Instructions",
            progress_percent=(17 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
            eyebrow="",
            heading="Instructions",
            paragraphs=[],
            bullets=[],
            secondary_bullets=[],
            instruction_lines=[
                dict(text="Each round of the game goes as follows:", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="1. Your IQ-rank is computed.", css_class=""),
                dict(text="2. You are informed whether your sender is high-status or low-status.", css_class=""),
                dict(text="3. The Sender is informed about a number that corresponds to your IQ-rank. For him/her, this number has no meaning.", css_class=""),
                dict(text="4. The Sender gives you information about this number.", css_class=""),
                dict(text="5. You receive this information and guess your IQ-rank.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="You earn more when your guess is closer to your IQ-rank. The Sender earns more when you guess a lower number.", css_class=""),
                dict(text="", css_class="spacer-line"),
                dict(text="No feedback: In the experiment, you will never receive more information about your IQ-ranks than the information given by the Senders.", css_class=""),
            ],
            button_label="Start Experiment",
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        assign_receiver_iq_rank_rounds(player)


class RoundStart(StaticInfoPage):
    @staticmethod
    def vars_for_template(player: Player):
        assign_receiver_iq_rank_rounds(player)
        return info_context(
            eyebrow="",
            heading="A new round is starting.",
            paragraphs=[
                (
                    "In this round, you will be randomly paired with another Sender."
                ),
                "Your task is to guess your IQ.",
            ],
            round_chip=f"Round {player.round_number} of {C.NUM_ROUNDS}",
            button_label="Next",
            **round_progress(player, 1),
        )


class SenderInformation(StaticInfoPage):
    @staticmethod
    def vars_for_template(player: Player):
        assign_receiver_iq_rank_rounds(player)
        return info_context(
            eyebrow="",
            heading="You are randomly paired with a sender",
            heading_class="compact-heading",
            paragraphs=["Sender's Status"],
            status_badge=player.sender_status,
            status_badge_class="status-badge-prominent",
            button_label="Next",
            **round_progress(player, 2),
        )


class ReceiverDecision(Page):
    form_model = "player"
    form_fields = ["guess"]

    @staticmethod
    def vars_for_template(player: Player):
        assign_receiver_iq_rank_rounds(player)
        available_numbers = sender_message_numbers(player.sender_message)
        return dict(
            round_label=f"Round {player.round_number} / {C.NUM_ROUNDS}",
            sender_status=player.sender_status,
            sender_message=receiver_message_display(player.sender_message),
            available_numbers_text=", ".join(str(number) for number in available_numbers),
            **round_progress(player, 3),
        )

    @staticmethod
    def error_message(player: Player, values):
        available_numbers = sender_message_numbers(player.sender_message)
        if values["guess"] not in available_numbers:
            allowed = ", ".join(str(number) for number in available_numbers)
            return f"Please enter one of the numbers sent by the Sender: {allowed}."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.payoff = (
            C.POINTS_FOR_CORRECT_GUESS
            if player.guess == player.sender_number
            else cu(0)
        )


class DemographicsIntro(StaticInfoPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return info_context(
            phase_label="",
            screen_counter="Introduction",
            progress_percent=(48 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
            eyebrow="",
            heading="One final section remains.",
            paragraphs=[
                "Before finishing the study, please complete a short demographic questionnaire.",
                "Your responses will remain confidential and will only be used for research purposes.",
            ],
            button_label="Start Questionnaire",
        )


class DemographicsQuestionnaire(Page):
    template_name = "receiver_experiment/Demographics.html"
    form_model = "player"
    form_fields = ["age", "gender", "education_level"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            phase_label="",
            screen_counter="Questionnaire",
            progress_percent=(49 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
        )


class StudyComplete(Page):
    template_name = "receiver_experiment/FinalRound.html"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        total_correct = sum(
            1
            for past_player in player.in_all_rounds()
            if past_player.field_maybe_none("guess") == past_player.sender_number
        )
        return dict(
            total_correct=total_correct,
            total_points=player.participant.payoff,
            iq_total=iq_score(player),
            phase_label="",
            screen_counter="Completed",
            progress_percent=(50 / C.TOTAL_EXPERIMENT_SCREENS) * 100,
        )


page_sequence = [
    Welcome,
    ParticipationInformation,
    IQIntro,
    IQQuestion1,
    IQQuestion2,
    IQQuestion3,
    IQQuestion4,
    IQQuestion5,
    IQQuestion6,
    IQQuestion7,
    IQQuestion8,
    IQQuestion9,
    IQQuestion10,
    IQEnd,
    Part2Intro,
    IQTransition,
    GameSummaryInstructions,
    RoundStart,
    SenderInformation,
    ReceiverDecision,
    DemographicsIntro,
    DemographicsQuestionnaire,
    StudyComplete,
]
