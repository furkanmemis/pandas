"""
Tests for the following offsets:
- CustomBusinessMonthBase
- CustomBusinessMonthBegin
- CustomBusinessMonthEnd
"""
from datetime import (
    date,
    datetime,
)

import numpy as np
import pytest

from pandas._libs.tslibs.offsets import (
    CBMonthBegin,
    CBMonthEnd,
    CDay,
)

from pandas import (
    _testing as tm,
    date_range,
)
from pandas.tests.tseries.offsets.common import (
    Base,
    assert_is_on_offset,
    assert_offset_equal,
)
from pandas.tests.tseries.offsets.test_offsets import _ApplyCases

from pandas.tseries import offsets as offsets
from pandas.tseries.holiday import USFederalHolidayCalendar


class CustomBusinessMonthBase:
    def setup_method(self, method):
        self.d = datetime(2008, 1, 1)
        self.offset = self._offset()
        self.offset1 = self.offset
        self.offset2 = self._offset(2)

    def test_eq(self):
        assert self.offset2 == self.offset2

    def test_mul(self):
        pass

    def test_hash(self):
        assert hash(self.offset2) == hash(self.offset2)

    def test_roundtrip_pickle(self):
        def _check_roundtrip(obj):
            unpickled = tm.round_trip_pickle(obj)
            assert unpickled == obj

        _check_roundtrip(self._offset())
        _check_roundtrip(self._offset(2))
        _check_roundtrip(self._offset() * 2)

    def test_copy(self):
        # GH 17452
        off = self._offset(weekmask="Mon Wed Fri")
        assert off == off.copy()


class TestCustomBusinessMonthBegin(CustomBusinessMonthBase, Base):
    _offset = CBMonthBegin

    def test_different_normalize_equals(self):
        # GH#21404 changed __eq__ to return False when `normalize` does not match
        offset = self._offset()
        offset2 = self._offset(normalize=True)
        assert offset != offset2

    def test_repr(self):
        assert repr(self.offset) == "<CustomBusinessMonthBegin>"
        assert repr(self.offset2) == "<2 * CustomBusinessMonthBegins>"

    def test_call(self):
        with tm.assert_produces_warning(FutureWarning):
            # GH#34171 DateOffset.__call__ is deprecated
            assert self.offset2(self.d) == datetime(2008, 3, 3)

    def testRollback1(self):
        assert CDay(10).rollback(datetime(2007, 12, 31)) == datetime(2007, 12, 31)

    def testRollback2(self):
        assert CBMonthBegin(10).rollback(self.d) == datetime(2008, 1, 1)

    def testRollforward1(self):
        assert CBMonthBegin(10).rollforward(self.d) == datetime(2008, 1, 1)

    def test_roll_date_object(self):
        offset = CBMonthBegin()

        dt = date(2012, 9, 15)

        result = offset.rollback(dt)
        assert result == datetime(2012, 9, 3)

        result = offset.rollforward(dt)
        assert result == datetime(2012, 10, 1)

        offset = offsets.Day()
        result = offset.rollback(dt)
        assert result == datetime(2012, 9, 15)

        result = offset.rollforward(dt)
        assert result == datetime(2012, 9, 15)

    on_offset_cases = [
        (CBMonthBegin(), datetime(2008, 1, 1), True),
        (CBMonthBegin(), datetime(2008, 1, 31), False),
    ]

    @pytest.mark.parametrize("case", on_offset_cases)
    def test_is_on_offset(self, case):
        offset, dt, expected = case
        assert_is_on_offset(offset, dt, expected)

    apply_cases: _ApplyCases = [
        (
            CBMonthBegin(),
            {
                datetime(2008, 1, 1): datetime(2008, 2, 1),
                datetime(2008, 2, 7): datetime(2008, 3, 3),
            },
        ),
        (
            2 * CBMonthBegin(),
            {
                datetime(2008, 1, 1): datetime(2008, 3, 3),
                datetime(2008, 2, 7): datetime(2008, 4, 1),
            },
        ),
        (
            -CBMonthBegin(),
            {
                datetime(2008, 1, 1): datetime(2007, 12, 3),
                datetime(2008, 2, 8): datetime(2008, 2, 1),
            },
        ),
        (
            -2 * CBMonthBegin(),
            {
                datetime(2008, 1, 1): datetime(2007, 11, 1),
                datetime(2008, 2, 9): datetime(2008, 1, 1),
            },
        ),
        (
            CBMonthBegin(0),
            {
                datetime(2008, 1, 1): datetime(2008, 1, 1),
                datetime(2008, 1, 7): datetime(2008, 2, 1),
            },
        ),
    ]

    @pytest.mark.parametrize("case", apply_cases)
    def test_apply(self, case):
        offset, cases = case
        for base, expected in cases.items():
            assert_offset_equal(offset, base, expected)

    def test_apply_large_n(self):
        dt = datetime(2012, 10, 23)

        result = dt + CBMonthBegin(10)
        assert result == datetime(2013, 8, 1)

        result = dt + CDay(100) - CDay(100)
        assert result == dt

        off = CBMonthBegin() * 6
        rs = datetime(2012, 1, 1) - off
        xp = datetime(2011, 7, 1)
        assert rs == xp

        st = datetime(2011, 12, 18)
        rs = st + off

        xp = datetime(2012, 6, 1)
        assert rs == xp

    def test_holidays(self):
        # Define a TradingDay offset
        holidays = ["2012-02-01", datetime(2012, 2, 2), np.datetime64("2012-03-01")]
        bm_offset = CBMonthBegin(holidays=holidays)
        dt = datetime(2012, 1, 1)

        assert dt + bm_offset == datetime(2012, 1, 2)
        assert dt + 2 * bm_offset == datetime(2012, 2, 3)

    @pytest.mark.filterwarnings("ignore:Non:pandas.errors.PerformanceWarning")
    def test_datetimeindex(self):
        hcal = USFederalHolidayCalendar()
        cbmb = CBMonthBegin(calendar=hcal)
        assert date_range(start="20120101", end="20130101", freq=cbmb).tolist()[
            0
        ] == datetime(2012, 1, 3)


class TestCustomBusinessMonthEnd(CustomBusinessMonthBase, Base):
    _offset = CBMonthEnd

    def test_different_normalize_equals(self):
        # GH#21404 changed __eq__ to return False when `normalize` does not match
        offset = self._offset()
        offset2 = self._offset(normalize=True)
        assert offset != offset2

    def test_repr(self):
        assert repr(self.offset) == "<CustomBusinessMonthEnd>"
        assert repr(self.offset2) == "<2 * CustomBusinessMonthEnds>"

    def test_call(self):
        with tm.assert_produces_warning(FutureWarning):
            # GH#34171 DateOffset.__call__ is deprecated
            assert self.offset2(self.d) == datetime(2008, 2, 29)

    def testRollback1(self):
        assert CDay(10).rollback(datetime(2007, 12, 31)) == datetime(2007, 12, 31)

    def testRollback2(self):
        assert CBMonthEnd(10).rollback(self.d) == datetime(2007, 12, 31)

    def testRollforward1(self):
        assert CBMonthEnd(10).rollforward(self.d) == datetime(2008, 1, 31)

    def test_roll_date_object(self):
        offset = CBMonthEnd()

        dt = date(2012, 9, 15)

        result = offset.rollback(dt)
        assert result == datetime(2012, 8, 31)

        result = offset.rollforward(dt)
        assert result == datetime(2012, 9, 28)

        offset = offsets.Day()
        result = offset.rollback(dt)
        assert result == datetime(2012, 9, 15)

        result = offset.rollforward(dt)
        assert result == datetime(2012, 9, 15)

    on_offset_cases = [
        (CBMonthEnd(), datetime(2008, 1, 31), True),
        (CBMonthEnd(), datetime(2008, 1, 1), False),
    ]

    @pytest.mark.parametrize("case", on_offset_cases)
    def test_is_on_offset(self, case):
        offset, d, expected = case
        assert_is_on_offset(offset, d, expected)

    apply_cases: _ApplyCases = [
        (
            CBMonthEnd(),
            {
                datetime(2008, 1, 1): datetime(2008, 1, 31),
                datetime(2008, 2, 7): datetime(2008, 2, 29),
            },
        ),
        (
            2 * CBMonthEnd(),
            {
                datetime(2008, 1, 1): datetime(2008, 2, 29),
                datetime(2008, 2, 7): datetime(2008, 3, 31),
            },
        ),
        (
            -CBMonthEnd(),
            {
                datetime(2008, 1, 1): datetime(2007, 12, 31),
                datetime(2008, 2, 8): datetime(2008, 1, 31),
            },
        ),
        (
            -2 * CBMonthEnd(),
            {
                datetime(2008, 1, 1): datetime(2007, 11, 30),
                datetime(2008, 2, 9): datetime(2007, 12, 31),
            },
        ),
        (
            CBMonthEnd(0),
            {
                datetime(2008, 1, 1): datetime(2008, 1, 31),
                datetime(2008, 2, 7): datetime(2008, 2, 29),
            },
        ),
    ]

    @pytest.mark.parametrize("case", apply_cases)
    def test_apply(self, case):
        offset, cases = case
        for base, expected in cases.items():
            assert_offset_equal(offset, base, expected)

    def test_apply_large_n(self):
        dt = datetime(2012, 10, 23)

        result = dt + CBMonthEnd(10)
        assert result == datetime(2013, 7, 31)

        result = dt + CDay(100) - CDay(100)
        assert result == dt

        off = CBMonthEnd() * 6
        rs = datetime(2012, 1, 1) - off
        xp = datetime(2011, 7, 29)
        assert rs == xp

        st = datetime(2011, 12, 18)
        rs = st + off
        xp = datetime(2012, 5, 31)
        assert rs == xp

    def test_holidays(self):
        # Define a TradingDay offset
        holidays = ["2012-01-31", datetime(2012, 2, 28), np.datetime64("2012-02-29")]
        bm_offset = CBMonthEnd(holidays=holidays)
        dt = datetime(2012, 1, 1)
        assert dt + bm_offset == datetime(2012, 1, 30)
        assert dt + 2 * bm_offset == datetime(2012, 2, 27)

    @pytest.mark.filterwarnings("ignore:Non:pandas.errors.PerformanceWarning")
    def test_datetimeindex(self):
        from pandas.tseries.holiday import USFederalHolidayCalendar

        hcal = USFederalHolidayCalendar()
        freq = CBMonthEnd(calendar=hcal)

        assert date_range(start="20120101", end="20130101", freq=freq).tolist()[
            0
        ] == datetime(2012, 1, 31)
