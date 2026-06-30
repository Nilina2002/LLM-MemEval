"""Unit tests for FactInjector and ConversationGenerator."""
from __future__ import annotations
import pytest

from app.core.config.experiment_config import FactConfig, ConversationConfig
from app.generators.fact_injector import FactInjector, FACT_TEMPLATES
from app.generators.conversation_generator import ConversationGenerator
from app.domain.entities.fact import FactType


class TestFactInjector:
    def setup_method(self):
        self.injector = FactInjector()

    def _config(self, count=5, types=None, seed=42):
        return FactConfig(
            count=count,
            types=types or ["personal", "technical", "temporal"],
            seed=seed,
        )

    def test_generates_expected_count(self):
        facts = self.injector.generate_facts(self._config(count=5))
        assert len(facts) == 5

    def test_facts_have_required_fields(self):
        facts = self.injector.generate_facts(self._config(count=3))
        for f in facts:
            assert f.fact_id
            assert f.text
            assert f.expected_answer
            assert f.recall_question
            assert isinstance(f.fact_type, FactType)
            assert 0.0 <= f.difficulty <= 1.0
            assert 0.0 <= f.importance <= 1.0

    def test_deterministic_with_same_seed(self):
        facts_a = self.injector.generate_facts(self._config(seed=123))
        facts_b = self.injector.generate_facts(self._config(seed=123))
        assert [f.text for f in facts_a] == [f.text for f in facts_b]
        assert [f.expected_answer for f in facts_a] == [f.expected_answer for f in facts_b]

    def test_different_seeds_produce_different_facts(self):
        facts_a = self.injector.generate_facts(self._config(seed=1))
        facts_b = self.injector.generate_facts(self._config(seed=99))
        # At least some facts should differ
        texts_a = [f.text for f in facts_a]
        texts_b = [f.text for f in facts_b]
        assert texts_a != texts_b

    def test_facts_have_unique_questions(self):
        facts = self.injector.generate_facts(self._config(count=8))
        questions = [f.recall_question for f in facts]
        assert len(questions) == len(set(questions)), "Questions should be unique within an experiment"

    def test_handles_single_type(self):
        facts = self.injector.generate_facts(self._config(types=["personal"]))
        assert all(f.fact_type == FactType.PERSONAL for f in facts)

    def test_text_contains_expected_answer(self):
        facts = self.injector.generate_facts(self._config(count=10))
        for f in facts:
            assert f.expected_answer in f.text, f"Expected answer '{f.expected_answer}' not in text '{f.text}'"

    def test_inject_sets_insertion_turn(self):
        gen = ConversationGenerator()
        config = ConversationConfig(domain="casual", total_turns=20, seed=42)
        facts = self.injector.generate_facts(self._config(count=3))
        positions = [5, 10, 15]
        conv = gen.generate(config, positions)
        conv, updated_facts = self.injector.inject_into_conversation(conv, facts)
        assert updated_facts[0].insertion_turn == 5
        assert updated_facts[1].insertion_turn == 10
        assert updated_facts[2].insertion_turn == 15

    def test_injection_replaces_slot_markers(self):
        gen = ConversationGenerator()
        config = ConversationConfig(domain="casual", total_turns=10, seed=42)
        facts = self.injector.generate_facts(self._config(count=2))
        positions = [3, 7]
        conv = gen.generate(config, positions)
        conv, _ = self.injector.inject_into_conversation(conv, facts)
        for turn in conv.turns:
            assert "[INJECT_SLOT_" not in turn.user_message, \
                f"Turn {turn.turn_number} still has slot marker"

    def test_wrapped_text_sounds_natural(self):
        facts = self.injector.generate_facts(self._config(count=5))
        gen = ConversationGenerator()
        config = ConversationConfig(domain="casual", total_turns=20, seed=42)
        positions = gen.calculate_injection_positions(20, 5, "uniform", 42)
        conv = gen.generate(config, positions)
        conv, updated = self.injector.inject_into_conversation(conv, facts)
        for f in updated:
            injected_turn = conv.get_turn(f.insertion_turn)
            assert injected_turn is not None
            assert f.expected_answer in injected_turn.user_message


class TestConversationGenerator:
    def setup_method(self):
        self.gen = ConversationGenerator()

    def _conv_config(self, domain="casual", turns=20, seed=42):
        return ConversationConfig(domain=domain, total_turns=turns, seed=seed)

    def test_generates_correct_turn_count(self):
        config = self._conv_config(turns=50)
        conv = self.gen.generate(config, [])
        assert len(conv.turns) == 50

    def test_turn_numbers_are_sequential(self):
        config = self._conv_config(turns=10)
        conv = self.gen.generate(config, [])
        for i, turn in enumerate(conv.turns):
            assert turn.turn_number == i + 1

    def test_injection_slots_marked_correctly(self):
        config = self._conv_config(turns=20)
        positions = [5, 10, 15]
        conv = self.gen.generate(config, positions)
        injection_turns = [t for t in conv.turns if t.is_injection_slot]
        assert len(injection_turns) == 3
        assert [t.turn_number for t in injection_turns] == positions

    def test_non_injection_turns_have_content(self):
        config = self._conv_config(turns=10)
        conv = self.gen.generate(config, [3])
        for turn in conv.turns:
            if not turn.is_injection_slot:
                assert turn.user_message.strip(), f"Turn {turn.turn_number} has empty user message"

    def test_deterministic_output(self):
        config = self._conv_config(turns=20, seed=7)
        conv_a = self.gen.generate(config, [5])
        conv_b = self.gen.generate(config, [5])
        for a, b in zip(conv_a.turns, conv_b.turns):
            assert a.user_message == b.user_message

    def test_different_seeds_produce_different_conversations(self):
        conv_a = self.gen.generate(self._conv_config(seed=1), [])
        conv_b = self.gen.generate(self._conv_config(seed=99), [])
        messages_a = [t.user_message for t in conv_a.turns]
        messages_b = [t.user_message for t in conv_b.turns]
        assert messages_a != messages_b

    def test_all_domains(self):
        for domain in ["casual", "programming", "education", "travel", "shopping", "mixed"]:
            config = ConversationConfig(domain=domain, total_turns=10, seed=42)
            conv = self.gen.generate(config, [])
            assert len(conv.turns) == 10

    def test_injection_positions_uniform(self):
        positions = self.gen.calculate_injection_positions(100, 5, "uniform", 42)
        assert len(positions) == 5
        assert positions == sorted(positions)

    def test_injection_positions_early(self):
        positions = self.gen.calculate_injection_positions(100, 5, "early", 42)
        assert len(positions) == 5
        assert max(positions) <= 30    # Early = first ~25% of turns

    def test_injection_positions_late(self):
        positions = self.gen.calculate_injection_positions(100, 5, "late", 42)
        assert len(positions) == 5
        assert min(positions) >= 60    # Late = last ~35% of turns

    def test_injection_positions_random(self):
        pos_a = self.gen.calculate_injection_positions(100, 5, "random", 1)
        pos_b = self.gen.calculate_injection_positions(100, 5, "random", 2)
        assert pos_a != pos_b          # Different seeds → different positions
