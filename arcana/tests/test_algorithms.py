import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from threads import Thread, EnergyThread, FormThread, TimeThread
from spells import WeaveSpell, CutSpell, BindSpell, LegendaryWeaveSpell, CombinedSpell, Rarity
from artifacts import CrystalCore, RuneMatrix
from caster import Caster, ArcaneInterface


@pytest.fixture
def basic_thread():
    return Thread("Тест", 100.0, 0.5)

@pytest.fixture
def energy_thread():
    return EnergyThread("Энергия", 200.0, 0.8, power=2.0)

@pytest.fixture
def form_thread():
    return FormThread("Форма", 150.0, 0.6, shape="куб")

@pytest.fixture
def time_thread():
    return TimeThread("Время", 100.0, 0.5, epoch=2)

@pytest.fixture
def weave_spell():
    return WeaveSpell("Плетение", cost=10)

@pytest.fixture
def cut_spell():
    return CutSpell("Разрыв", cost=8, severity=0.3)

@pytest.fixture
def bind_spell():
    return BindSpell("Оковы", cost=15, duration=5)

@pytest.fixture
def legendary_spell():
    return LegendaryWeaveSpell("Легенда", cost=30)

@pytest.fixture
def caster(weave_spell):
    c = Caster("Варн", energy=100)
    c.learn(weave_spell)
    return c

@pytest.fixture
def crystal_core():
    return CrystalCore()

@pytest.fixture
def rune_matrix():
    return RuneMatrix(capacity=3)


class TestThread:
    def test_thread_created_with_valid_values(self, basic_thread):
        assert basic_thread.frequency == 998.0
        assert basic_thread.stability == 0.5
        assert basic_thread.name == "Тест"

    def test_thread_raises_value_error_on_negative_frequency(self):
        with pytest.raises(ValueError):
            Thread("X", -1.0, 0.5)

    def test_thread_raises_value_error_on_frequency_too_high(self):
        with pytest.raises(ValueError):
            Thread("X", 1000.0, 0.5)

    def test_thread_raises_value_error_on_stability_above_one(self):
        with pytest.raises(ValueError):
            Thread("X", 100.0, 1.5)

    def test_thread_raises_value_error_on_negative_stability(self):
        with pytest.raises(ValueError):
            Thread("X", 100.0, -0.1)

    def test_thread_min_boundary_frequency(self):
        t = Thread("X", 0.1, 0.5)
        assert t.frequency == 0.1

    def test_thread_max_boundary_frequency(self):
        t = Thread("X", 999.9, 0.5)
        assert t.frequency == 999.9

    def test_thread_min_boundary_stability(self):
        t = Thread("X", 100.0, 0.0)
        assert t.stability == 0.0

    def test_thread_max_boundary_stability(self):
        t = Thread("X", 100.0, 1.0)
        assert t.stability == 1.0

    def test_thread_setter_updates_frequency(self, basic_thread):
        basic_thread.frequency = 200.0
        assert basic_thread.frequency == 200.0

    def test_thread_setter_raises_on_invalid_update(self, basic_thread):
        with pytest.raises(ValueError):
            basic_thread.frequency = 0.0

    def test_thread_resonate_returns_float(self, basic_thread, energy_thread):
        result = basic_thread.resonate(energy_thread)
        assert isinstance(result, float)

    def test_thread_add_creates_new_thread(self, basic_thread, form_thread):
        result = basic_thread + form_thread
        assert isinstance(result, Thread)

    def test_thread_add_frequency_is_average(self, basic_thread, form_thread):
        result = basic_thread + form_thread
        expected = (basic_thread.frequency + form_thread.frequency) / 2
        assert result.frequency == pytest.approx(expected)

    def test_thread_str_contains_name(self, basic_thread):
        assert "Тест" in str(basic_thread)

    def test_thread_repr_contains_frequency(self, basic_thread):
        assert "100.0" in repr(basic_thread)


class TestEnergyThread:
    def test_energy_thread_resonate_uses_power(self, energy_thread, form_thread):
        result = energy_thread.resonate(form_thread)
        assert result > 0

    def test_energy_thread_str_contains_power(self, energy_thread):
        assert "power" in str(energy_thread)


class TestFormThread:
    def test_form_thread_resonate_adds_shape_len(self, form_thread, basic_thread):
        result = form_thread.resonate(basic_thread)
        base = Thread.resonate(form_thread, basic_thread)
        assert result == pytest.approx(base + len("куб") - (base - (Thread("tmp", form_thread.frequency, form_thread.stability).resonate(basic_thread))))

    def test_form_thread_str_contains_shape(self, form_thread):
        assert "куб" in str(form_thread)


class TestTimeThread:
    def test_time_thread_resonate_divides_by_epoch(self, time_thread, basic_thread):
        result = time_thread.resonate(basic_thread)
        assert result > 0

    def test_time_thread_str_contains_epoch(self, time_thread):
        assert "epoch" in str(time_thread)


class TestSpells:
    def test_weave_spell_cast_returns_string(self, weave_spell, caster):
        result = weave_spell.cast(caster, "цель")
        assert isinstance(result, str)

    def test_weave_spell_cast_reduces_energy(self, weave_spell, caster):
        initial = caster.energy
        weave_spell.cast(caster, "цель")
        assert caster.energy == initial - weave_spell.cost

    def test_cut_spell_cast_returns_string(self, cut_spell, caster):
        result = cut_spell.cast(caster, "цель")
        assert isinstance(result, str)

    def test_bind_spell_cast_returns_string(self, bind_spell, caster):
        result = bind_spell.cast(caster, "цель")
        assert isinstance(result, str)

    def test_legendary_spell_cast_contains_legendary(self, legendary_spell, caster):
        result = legendary_spell.cast(caster, "цель")
        assert "LEGENDARY" in result

    def test_legendary_spell_is_legendary_rarity(self, legendary_spell):
        assert legendary_spell.rarity == Rarity.LEGENDARY

    def test_spell_gt_legendary_greater_than_common(self, legendary_spell, weave_spell):
        assert legendary_spell > weave_spell

    def test_spell_gt_common_not_greater_than_legendary(self, weave_spell, legendary_spell):
        assert not (weave_spell > legendary_spell)

    def test_combined_spell_casts_all(self, weave_spell, cut_spell, caster):
        combo = CombinedSpell("Комбо", [weave_spell, cut_spell])
        result = combo.cast(caster, "цель")
        assert isinstance(result, str)
        assert "|" in result

    def test_combined_spell_describe(self, weave_spell, cut_spell):
        combo = CombinedSpell("Комбо", [weave_spell, cut_spell])
        desc = combo.describe()
        assert "Комбо" in desc

    def test_weave_spell_describe(self, weave_spell):
        assert "Плетение" in weave_spell.describe()

    def test_cut_spell_describe(self, cut_spell):
        assert "Разрыв" in cut_spell.describe()

    def test_bind_spell_describe(self, bind_spell):
        assert "Оковы" in bind_spell.describe()


class TestArtifacts:
    def test_crystal_core_activate_returns_float(self, crystal_core, basic_thread):
        result = crystal_core.activate(basic_thread)
        assert isinstance(result, float)

    def test_crystal_core_durability_decreases(self, crystal_core, basic_thread):
        initial = crystal_core.durability
        crystal_core.activate(basic_thread)
        assert crystal_core.durability == initial - 2

    def test_rune_matrix_store_and_activate(self, rune_matrix, basic_thread, energy_thread):
        rune_matrix.store(basic_thread)
        rune_matrix.store(energy_thread)
        result = rune_matrix.activate(basic_thread)
        assert result > 0

    def test_rune_matrix_capacity_limit(self, rune_matrix, basic_thread):
        for _ in range(5):
            rune_matrix.store(basic_thread)
        assert len(rune_matrix._stored) == 3

    def test_crystal_core_durability_not_negative(self, crystal_core, basic_thread):
        crystal_core.durability = 1
        crystal_core.activate(basic_thread)
        assert crystal_core.durability >= 0

    def test_crystal_core_str(self, crystal_core):
        assert "CrystalCore" in str(crystal_core)


class TestCaster:
    def test_caster_learn_adds_spell(self, caster, cut_spell):
        initial = len(caster)
        caster.learn(cut_spell)
        assert len(caster) == initial + 1

    def test_caster_forget_removes_spell(self, caster, weave_spell):
        caster.forget(weave_spell.name)
        assert len(caster) == 0

    def test_caster_cast_known_spell(self, caster):
        result = caster.cast("Плетение", "цель")
        assert isinstance(result, str)
        assert "не найдено" not in result

    def test_caster_cast_unknown_spell(self, caster):
        result = caster.cast("Несуществующее", "цель")
        assert "not found" in result

    def test_caster_len_returns_spell_count(self, caster):
        assert len(caster) == 1

    def test_caster_equip_sets_artifact(self, crystal_core):
        c = Caster("Тест", energy=50)
        c.equip(crystal_core)
        assert c.artifact == crystal_core

    def test_caster_equip_warns_on_replace(self, crystal_core, rune_matrix, capsys):
        c = Caster("Тест", energy=50)
        c.equip(crystal_core)
        c.equip(rune_matrix)
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_caster_str_returns_name(self, caster):
        assert "Варн" in str(caster)


class TestMocks:
    def test_mock_patch_crystal_core_activate(self, basic_thread):
        with patch('artifacts.CrystalCore.activate') as mock_activate:
            mock_activate.return_value = 99.9
            core = CrystalCore()
            result = core.activate(basic_thread)
            assert result == 99.9
            mock_activate.assert_called_once()

    def test_magic_mock_spell_cast_called_with_args(self):
        mock_spell = MagicMock()
        mock_spell.cast.return_value = "результат"
        caster = Caster("Тест", energy=50)
        result = mock_spell.cast(caster, "цель")
        mock_spell.cast.assert_called_once_with(caster, "цель")
        assert result == "результат"

    def test_side_effect_raises_exception(self, basic_thread):
        with patch('artifacts.CrystalCore.activate') as mock_activate:
            mock_activate.side_effect = RuntimeError("Артефакт сломан")
            core = CrystalCore()
            with pytest.raises(RuntimeError, match="Артефакт сломан"):
                core.activate(basic_thread)


class TestLogging:
    def test_logging_called_on_invalid_frequency(self):
        with patch('threads.logging.error') as mock_log:
            with pytest.raises(ValueError):
                Thread("X", -5.0, 0.5)
            mock_log.assert_called_once()

    def test_logging_message_contains_invalid_value(self):
        with patch('threads.logging.error') as mock_log:
            with pytest.raises(ValueError):
                Thread("X", -5.0, 0.5)
            args = mock_log.call_args[0][0]
            assert "-5.0" in args

    def test_logging_called_on_invalid_stability(self):
        with patch('threads.logging.error') as mock_log:
            with pytest.raises(ValueError):
                Thread("X", 100.0, 2.0)
            mock_log.assert_called_once()


class TestPolymorphism:
    def test_execute_all_works_with_mixed_spells(self, weave_spell, cut_spell, legendary_spell):
        def execute_all(spells, caster, target):
            return [s.cast(caster, target) for s in spells]

        caster = Caster("Тест", energy=200)
        results = execute_all([weave_spell, cut_spell, legendary_spell], caster, "цель")
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)

    def test_arcane_interface_protocol(self, weave_spell):
        assert isinstance(weave_spell, ArcaneInterface)

    def test_combined_spell_polymorphic_with_single(self, weave_spell, cut_spell):
        combo = CombinedSpell("Комбо", [weave_spell, cut_spell])
        caster = Caster("Тест", energy=200)
        result = combo.cast(caster, "цель")
        assert isinstance(result, str)
