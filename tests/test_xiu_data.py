"""Tests for renderer3d/xiu_data.py - star map data integrity."""
import pytest
from renderer3d.xiu_data import (
    ALL_MANSIONS_ORDERED, ORDERED_NAMES,
    BEAST_OUTLINES, BEAST_QUADRANTS,
    MansionData, BeastOutline,
)
from config import ORDERED_XIU_R


# ── 28 Mansion basic checks ──

class TestMansionCount:
    def test_exactly_28_mansions(self):
        assert len(ALL_MANSIONS_ORDERED) == 28

    def test_names_match_config_order(self):
        """ALL_MANSIONS_ORDERED names must match ORDERED_XIU_R exactly."""
        assert ORDERED_NAMES == list(ORDERED_XIU_R)

    def test_all_are_mansion_data(self):
        for m in ALL_MANSIONS_ORDERED:
            assert isinstance(m, MansionData)

    def test_no_duplicate_names(self):
        assert len(set(ORDERED_NAMES)) == 28


# ── Star counts per mansion ──

EXPECTED_STAR_COUNTS = {
    '角': 2, '亢': 4, '氐': 4, '房': 4, '心': 3, '尾': 6, '箕': 4,   # 东 27
    '斗': 6, '牛': 6, '女': 4, '虚': 2, '危': 3, '室': 2, '壁': 2,   # 北 25
    '奎': 8, '娄': 3, '胃': 3, '昴': 6, '毕': 6, '觜': 3, '参': 7,   # 西 36
    '井': 8, '鬼': 4, '柳': 6, '星': 7, '张': 6, '翼': 6, '轸': 4,   # 南 41
}

class TestStarCounts:
    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_star_count(self, mansion):
        expected = EXPECTED_STAR_COUNTS[mansion.name]
        assert len(mansion.star_offsets) == expected, (
            f"{mansion.name}: expected {expected} stars, got {len(mansion.star_offsets)}"
        )

    def test_total_star_count(self):
        total = sum(len(m.star_offsets) for m in ALL_MANSIONS_ORDERED)
        assert total == sum(EXPECTED_STAR_COUNTS.values())

    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_each_mansion_has_at_least_one_star(self, mansion):
        assert len(mansion.star_offsets) >= 1


# ── Line index validation ──

class TestLineIndices:
    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_line_indices_in_range(self, mansion):
        n_stars = len(mansion.star_offsets)
        for i, (a, b) in enumerate(mansion.lines):
            assert 0 <= a < n_stars, (
                f"{mansion.name} line {i}: index {a} out of range [0, {n_stars})"
            )
            assert 0 <= b < n_stars, (
                f"{mansion.name} line {i}: index {b} out of range [0, {n_stars})"
            )

    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_no_self_loops(self, mansion):
        for a, b in mansion.lines:
            assert a != b, f"{mansion.name}: self-loop ({a}, {b})"

    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_has_at_least_one_line(self, mansion):
        assert len(mansion.lines) >= 1


# ── Star offset ranges ──

class TestStarOffsets:
    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_dr_in_range(self, mansion):
        for i, (dr, _) in enumerate(mansion.star_offsets):
            assert -0.20 <= dr <= 0.20, (
                f"{mansion.name} star {i}: dr={dr} out of range"
            )

    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_dtheta_in_range(self, mansion):
        for i, (_, dtheta) in enumerate(mansion.star_offsets):
            assert -5.0 <= dtheta <= 5.0, (
                f"{mansion.name} star {i}: dtheta={dtheta} out of range"
            )

    @pytest.mark.parametrize("mansion", ALL_MANSIONS_ORDERED,
                             ids=[m.name for m in ALL_MANSIONS_ORDERED])
    def test_anchor_star_at_origin(self, mansion):
        """First star (anchor) should be at or near origin."""
        dr, dtheta = mansion.star_offsets[0]
        assert abs(dr) <= 0.02 and abs(dtheta) <= 0.5, (
            f"{mansion.name} anchor star not at origin: ({dr}, {dtheta})"
        )


# ── Beast outlines ──

class TestBeastOutlines:
    def test_exactly_4_beasts(self):
        assert len(BEAST_OUTLINES) == 4

    def test_beast_keys(self):
        assert set(BEAST_OUTLINES.keys()) == {'dragon', 'tortoise', 'tiger', 'bird'}

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_is_outline_type(self, key):
        assert isinstance(BEAST_OUTLINES[key], BeastOutline)

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_has_vertices(self, key):
        assert len(BEAST_OUTLINES[key].vertices) >= 50

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_has_lines(self, key):
        assert len(BEAST_OUTLINES[key].lines) >= 50

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_line_indices_in_range(self, key):
        outline = BEAST_OUTLINES[key]
        n_verts = len(outline.vertices)
        for i, (a, b) in enumerate(outline.lines):
            assert 0 <= a < n_verts, (
                f"{key} line {i}: index {a} out of range [0, {n_verts})"
            )
            assert 0 <= b < n_verts, (
                f"{key} line {i}: index {b} out of range [0, {n_verts})"
            )

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_color_rgba(self, key):
        color = BEAST_OUTLINES[key].color
        assert len(color) == 4
        for c in color:
            assert 0.0 <= c <= 1.0

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_r_fraction_range(self, key):
        for i, (r, _) in enumerate(BEAST_OUTLINES[key].vertices):
            assert 0.5 <= r <= 1.5, (
                f"{key} vertex {i}: r_fraction={r} out of range"
            )

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_beast_theta_range(self, key):
        for i, (_, theta) in enumerate(BEAST_OUTLINES[key].vertices):
            assert -50.0 <= theta <= 50.0, (
                f"{key} vertex {i}: theta_deg={theta} out of range"
            )


# ── Beast quadrant indices ──

class TestBeastQuadrants:
    def test_exactly_4_quadrants(self):
        assert len(BEAST_QUADRANTS) == 4

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_7_mansions_per_quadrant(self, key):
        assert len(BEAST_QUADRANTS[key]['indices']) == 7

    @pytest.mark.parametrize("key", ['dragon', 'tortoise', 'tiger', 'bird'])
    def test_quadrant_indices_in_range(self, key):
        for idx in BEAST_QUADRANTS[key]['indices']:
            assert 0 <= idx <= 27

    def test_all_28_covered(self):
        all_indices = set()
        for q in BEAST_QUADRANTS.values():
            all_indices.update(q['indices'])
        assert len(all_indices) == 28

    def test_chinese_names(self):
        expected_names = {'青龙', '玄武', '白虎', '朱雀'}
        actual_names = {BEAST_OUTLINES[k].name for k in BEAST_OUTLINES}
        assert actual_names == expected_names
