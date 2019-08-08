# -*- coding: utf-8 -*-
import pytest
import datetime
import copy

import numpy as np
import astropy.units as u
import matplotlib
try:
    from sunpy.visualization.animator import ImageAnimatorWCS, LineAnimator
except ImportError:
    from sunpy.visualization.imageanimator import ImageAnimatorWCS, LineAnimator

from ndcube import NDCube
from ndcube.utils.wcs import WCS
from ndcube.mixins import plotting


# sample data for tests
# TODO: use a fixture reading from a test file. file TBD.
ht = {'CTYPE3': 'HPLT-TAN', 'CUNIT3': 'deg', 'CDELT3': 0.5, 'CRPIX3': 0, 'CRVAL3': 0, 'NAXIS3': 2,
      'CTYPE2': 'WAVE    ', 'CUNIT2': 'Angstrom', 'CDELT2': 0.2, 'CRPIX2': 0, 'CRVAL2': 0,
      'NAXIS2': 3,
      'CTYPE1': 'TIME    ', 'CUNIT1': 'min', 'CDELT1': 0.4, 'CRPIX1': 0, 'CRVAL1': 0, 'NAXIS1': 4}
wt = WCS(header=ht, naxis=3)

hm = {'CTYPE1': 'WAVE    ', 'CUNIT1': 'Angstrom', 'CDELT1': 0.2, 'CRPIX1': 0, 'CRVAL1': 10,
      'NAXIS1': 4,
      'CTYPE2': 'HPLT-TAN', 'CUNIT2': 'deg', 'CDELT2': 0.5, 'CRPIX2': 2, 'CRVAL2': 0.5,
      'NAXIS2': 3,
      'CTYPE3': 'HPLN-TAN', 'CUNIT3': 'deg', 'CDELT3': 0.4, 'CRPIX3': 2, 'CRVAL3': 1, 'NAXIS3': 2}
wm = WCS(header=hm, naxis=3)

data = np.array([[[1, 2, 3, 4], [2, 4, 5, 3], [0, -1, 2, 3]],
                 [[2, 4, 5, 1], [10, 5, 2, 2], [10, 3, 3, 0]]])

uncertainty = np.sqrt(data)
mask_cube = data < 0

cube = NDCube(
    data,
    wt,
    mask=mask_cube,
    uncertainty=uncertainty,
    missing_axes=[False, False, False, True],
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.s)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.W)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.m)),
                  ('another time', 2, np.array(
                      [datetime.datetime(2000, 1, 1)+datetime.timedelta(minutes=i)
                       for i in range(data.shape[2])])),
                  ('array coord', 2, np.arange(100, 100+data.shape[2]))
                  ])

cube_unit = NDCube(
    data,
    wt,
    mask=mask_cube,
    unit=u.J,
    uncertainty=uncertainty,
    missing_axes=[False, False, False, True],
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.s)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.W)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.m)),
                  ('another time', 2, np.array(
                      [datetime.datetime(2000, 1, 1)+datetime.timedelta(minutes=i)
                       for i in range(data.shape[2])]))
                  ])

cube_no_uncertainty = NDCube(
    data,
    wt,
    mask=mask_cube,
    missing_axes=[False, False, False, True],
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.s)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.W)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.m)),
                  ('another time', 2, np.array(
                      [datetime.datetime(2000, 1, 1)+datetime.timedelta(minutes=i)
                       for i in range(data.shape[2])]))
                  ])

cube_unit_no_uncertainty = NDCube(
    data,
    wt,
    mask=mask_cube,
    unit=u.J,
    missing_axes=[False, False, False, True],
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.s)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.W)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.m)),
                  ('another time', 2, np.array(
                      [datetime.datetime(2000, 1, 1)+datetime.timedelta(minutes=i)
                       for i in range(data.shape[2])]))
                  ])

cubem = NDCube(
    data,
    wm,
    mask=mask_cube,
    uncertainty=uncertainty,
    extra_coords=[('time', 0, u.Quantity(range(data.shape[0]), unit=u.s)),
                  ('hello', 1, u.Quantity(range(data.shape[1]), unit=u.W)),
                  ('bye', 2, u.Quantity(range(data.shape[2]), unit=u.m)),
                  ('another time', 2, np.array(
                      [datetime.datetime(2000, 1, 1)+datetime.timedelta(minutes=i)
                       for i in range(data.shape[2])]))
                  ])

# Derive expected data values
cube_data = np.ma.masked_array(cube.data, cube.mask)

# Derive expected axis_ranges.
# Let False stand for ranges generated by SunPy classes and so not tested.
cube_none_axis_ranges_axis2 = [False, False, np.array([0.4, 0.8, 1.2, 1.6])]

cube_none_axis_ranges_axis2_s = copy.deepcopy(cube_none_axis_ranges_axis2)
cube_none_axis_ranges_axis2_s[2] = cube_none_axis_ranges_axis2[2] * 60.

cube_none_axis_ranges_axis2_bye = copy.deepcopy(cube_none_axis_ranges_axis2)
cube_none_axis_ranges_axis2_bye[2] = cube.extra_coords["bye"]["value"].value

cube_none_axis_ranges_axis2_array = copy.deepcopy(cube_none_axis_ranges_axis2)
cube_none_axis_ranges_axis2_array[2] = np.arange(10, 10+cube.data.shape[-1])

@pytest.mark.parametrize("test_input, test_kwargs, expected_values", [
    (cube[0, 0], {},
     (np.ma.masked_array([0.4, 0.8, 1.2, 1.6], cube[0, 0].mask),
      np.ma.masked_array(cube[0, 0].data, cube[0, 0].mask),
      "time [min]", "Data [None]", (0.4, 1.6), (1, 4))),

    (cube_unit[0, 0], {"axes_coordinates": "bye", "axes_units": "km", "data_unit": u.erg},
     (np.ma.masked_array(cube_unit[0, 0].extra_coords["bye"]["value"].to(u.km).value,
                         cube_unit[0, 0].mask),
      np.ma.masked_array(u.Quantity(cube_unit[0, 0].data,
                                    unit=cube_unit[0, 0].unit).to(u.erg).value,
                         cube_unit[0, 0].mask),
      "bye [km]", "Data [erg]", (0, 0.003), (10000000, 40000000))),

    (cube_unit[0, 0], {"axes_coordinates": np.arange(10, 10+cube_unit[0, 0].data.shape[0])},
     (np.ma.masked_array(np.arange(10, 10+cube_unit[0, 0].data.shape[0]), cube_unit[0, 0].mask),
      np.ma.masked_array(cube_unit[0, 0].data, cube_unit[0, 0].mask),
      " [None]", "Data [J]", (10, 10+cube_unit[0, 0].data.shape[0]-1), (1, 4))),

    (cube_no_uncertainty[0, 0], {},
     (np.ma.masked_array([0.4, 0.8, 1.2, 1.6], cube_no_uncertainty[0, 0].mask),
      np.ma.masked_array(cube_no_uncertainty[0, 0].data, cube_no_uncertainty[0, 0].mask),
      "time [min]", "Data [None]", (0.4, 1.6), (1, 4))),

    (cube_unit_no_uncertainty[0, 0], {},
     (np.ma.masked_array([0.4, 0.8, 1.2, 1.6], cube_unit_no_uncertainty[0, 0].mask),
      np.ma.masked_array(cube_no_uncertainty[0, 0].data, cube_unit_no_uncertainty[0, 0].mask),
      "time [min]", "Data [J]", (0.4, 1.6), (1, 4))),

    (cube_unit_no_uncertainty[0, 0], {"data_unit": u.erg},
     (np.ma.masked_array([0.4, 0.8, 1.2, 1.6], cube_unit_no_uncertainty[0, 0].mask),
      np.ma.masked_array(u.Quantity(cube_unit[0, 0].data,
                                    unit=cube_unit[0, 0].unit).to(u.erg).value,
                         cube_unit[0, 0].mask),
      "time [min]", "Data [erg]", (0.4, 1.6), (10000000, 40000000)))
    ])
def test_cube_plot_1D(test_input, test_kwargs, expected_values):
    # Unpack expected properties.
    expected_xdata, expected_ydata, expected_xlabel, expected_ylabel, \
      expected_xlim, expected_ylim = expected_values
    # Run plot method.
    output = test_input.plot(**test_kwargs)
    # Check plot properties are correct.
    # Type
    assert isinstance(output, matplotlib.axes.Axes)
    # Check x axis data
    output_xdata = (output.axes.lines[0].get_xdata())
    assert np.allclose(output_xdata.data, expected_xdata.data)
    if isinstance(output_xdata.mask, np.ndarray):
        np.testing.assert_array_equal(output_xdata.mask, expected_xdata.mask)
    else:
        assert output_xdata.mask == expected_xdata.mask
    # Check y axis data
    output_ydata = (output.axes.lines[0].get_ydata())
    assert np.allclose(output_ydata.data, expected_ydata.data)
    if isinstance(output_ydata.mask, np.ndarray):
        np.testing.assert_array_equal(output_ydata.mask, expected_ydata.mask)
    else:
        assert output_ydata.mask == expected_ydata.mask
    # Check axis labels
    assert output.axes.get_xlabel() == expected_xlabel
    assert output.axes.get_ylabel() == expected_ylabel
    # Check axis limits
    output_xlim = output.axes.get_xlim()
    assert output_xlim[0] <= expected_xlim[0]
    assert output_xlim[1] >= expected_xlim[1]
    output_ylim = output.axes.get_ylim()
    assert output_ylim[0] <= expected_ylim[0]
    assert output_ylim[1] >= expected_ylim[1]


@pytest.mark.parametrize("test_input, test_kwargs, expected_error", [
    (cube[0, 0], {"axes_coordinates": np.arange(10, 10+cube_unit[0, 0].data.shape[0]),
                  "axes_units": u.C}, TypeError),
    (cube[0, 0], {"data_unit": u.C}, TypeError)
    ])
def test_cube_plot_1D_errors(test_input, test_kwargs, expected_error):
    with pytest.raises(expected_error):
        output = test_input.plot(**test_kwargs)


@pytest.mark.parametrize("test_input, test_kwargs, expected_values", [
    (cube[0], {},
     (np.ma.masked_array(cube[0].data, cube[0].mask), "time [min]", "em.wl [m]",
      (-0.5, 3.5, 2.5, -0.5))),

    (cube[0], {"axes_coordinates": ["bye", None], "axes_units": [None, u.cm]},
     (np.ma.masked_array(cube[0].data, cube[0].mask), "bye [m]", "em.wl [cm]",
      (0.0, 3.0, 2e-9, 6e-9))),

    (cube[0], {"axes_coordinates": [np.arange(10, 10+cube[0].data.shape[1]),
                                    u.Quantity(np.arange(10, 10+cube[0].data.shape[0]), unit=u.m)],
               "axes_units": [None, u.cm]},
     (np.ma.masked_array(cube[0].data, cube[0].mask), " [None]", " [cm]", (10, 13, 1000, 1200))),

    (cube[0], {"axes_coordinates": [np.arange(10, 10+cube[0].data.shape[1]),
                                    u.Quantity(np.arange(10, 10+cube[0].data.shape[0]), unit=u.m)]},
     (np.ma.masked_array(cube[0].data, cube[0].mask), " [None]", " [m]", (10, 13, 10, 12))),

    (cube_unit[0], {"plot_axis_indices": [0, 1], "axes_coordinates": [None, "bye"],
                    "data_unit": u.erg},
     (np.ma.masked_array((cube_unit[0].data * cube_unit[0].unit).to(u.erg).value,
                         cube_unit[0].mask).transpose(),
      "em.wl [m]", "bye [m]", (2e-11, 6e-11, 0.0, 3.0)))
    ])
def test_cube_plot_2D(test_input, test_kwargs, expected_values):
    # Unpack expected properties.
    expected_data, expected_xlabel, expected_ylabel, expected_extent = \
      expected_values
    # Run plot method.
    output = test_input.plot(**test_kwargs)
    # Check plot properties are correct.
    assert isinstance(output, matplotlib.axes.Axes)
    np.testing.assert_array_equal(output.images[0].get_array(), expected_data)
    assert output.axes.xaxis.get_label_text() == expected_xlabel
    assert output.axes.yaxis.get_label_text() == expected_ylabel
    assert np.allclose(output.images[0].get_extent(), expected_extent)


@pytest.mark.parametrize("test_input, test_kwargs, expected_error", [
    (cube[0], {"axes_coordinates": ["array coord", None], "axes_units": [u.cm, None]}, TypeError),
    (cube[0], {"axes_coordinates": [np.arange(10, 10+cube[0].data.shape[1]), None],
               "axes_units": [u.cm, None]}, TypeError),
    (cube[0], {"data_unit": u.cm}, TypeError)
    ])
def test_cube_plot_2D_errors(test_input, test_kwargs, expected_error):
    with pytest.raises(expected_error):
        output = test_input.plot(**test_kwargs)


@pytest.mark.parametrize("test_input, test_kwargs, expected_values", [
    (cubem, {},
     (cubem.data, [np.array([0., 2.]), [0, 3], [0, 4]], "", ""))
    ])
def test_cube_plot_ND_as_2DAnimation(test_input, test_kwargs, expected_values):
    # Unpack expected properties.
    expected_data, expected_axis_ranges, expected_xlabel, expected_ylabel = expected_values
    # Run plot method.
    output = test_input.plot(**test_kwargs)
    # Check plot properties are correct.
    assert type(output) is ImageAnimatorWCS
    np.testing.assert_array_equal(output.data, expected_data)
    assert output.axes.xaxis.get_label_text() == expected_xlabel
    assert output.axes.yaxis.get_label_text() == expected_ylabel


@pytest.mark.parametrize("input_values, expected_values", [
    ((None, None, None, None, {"image_axes": [-1, -2],
                               "axis_ranges": [np.arange(3), np.arange(3)],
                               "unit_x_axis": "km",
                               "unit_y_axis": u.s,
                               "unit": u.W}),
     ([-1, -2], [np.arange(3), np.arange(3)], ["km", u.s], u.W, {})),
    (([-1, -2], [np.arange(3), np.arange(3)], ["km", u.s], u.W, {}),
     ([-1, -2], [np.arange(3), np.arange(3)], ["km", u.s], u.W, {})),
    (([-1], None, None, None, {"unit_x_axis": "km"}),
     ([-1], None, "km", None, {})),
    (([-1, -2], None, None, None, {"unit_x_axis": "km"}),
     (([-1, -2], None, ["km", None], None, {}))),
    (([-1, -2], None, None, None, {"unit_y_axis": "km"}),
     (([-1, -2], None, [None, "km"], None, {})))
    ])
def test_support_101_plot_API(input_values, expected_values):
    # Define expected values.
    expected_plot_axis_indices, expected_axes_coordinates, expected_axes_units, \
      expected_data_unit, expected_kwargs = expected_values
    # Run function
    output_plot_axis_indices, output_axes_coordinates, output_axes_units, \
      output_data_unit, output_kwargs = plotting._support_101_plot_API(*input_values)
    # Check values are correct
    assert output_plot_axis_indices == expected_plot_axis_indices
    if expected_axes_coordinates is None:
        assert output_axes_coordinates == expected_axes_coordinates
    elif type(expected_axes_coordinates) is list:
        for i, ac in enumerate(output_axes_coordinates):
            np.testing.assert_array_equal(ac, expected_axes_coordinates[i])
    assert output_axes_units == expected_axes_units
    assert output_data_unit == expected_data_unit
    assert output_kwargs == expected_kwargs


@pytest.mark.parametrize("input_values", [
    ([0, 1], None, None, None, {"image_axes": [-1, -2]}),
    (None, [np.arange(1, 4), np.arange(1, 4)], None, None,
      {"axis_ranges": [np.arange(3), np.arange(3)]}),
    (None, None, [u.s, "km"], None, {"unit_x_axis": u.W}),
    (None, None, [u.s, "km"], None, {"unit_y_axis": u.W}),
    (None, None, None, u.s, {"unit": u.W}),
    ([0, 1, 2], None, None, None, {"unit_x_axis": [u.s, u.km, u.W]}),
    ])
def test_support_101_plot_API_errors(input_values):
    with pytest.raises(ValueError):
        output = plotting._support_101_plot_API(*input_values)


@pytest.mark.parametrize("test_input, test_kwargs, expected_values", [
    (cube, {"plot_axis_indices": -1},
     (cube_data, cube_none_axis_ranges_axis2, "time [min]", "Data [None]")),

    (cube_unit, {"plot_axis_indices": -1, "axes_units": u.s, "data_unit": u.erg},
     (cube_data*1e7, cube_none_axis_ranges_axis2_s, "time [s]", "Data [erg]")),

    (cube_unit, {"plot_axis_indices": -1, "axes_coordinates": "bye"},
     (cube_data, cube_none_axis_ranges_axis2_bye, "bye [m]", "Data [J]")),

    (cube, {"plot_axis_indices": -1, "axes_coordinates": np.arange(10 - 0.5, 0.5+10 + cube.data.shape[-1])},
     (cube_data, cube_none_axis_ranges_axis2_array, " [None]", "Data [None]"))
    ])
def test_cube_plot_ND_as_1DAnimation(test_input, test_kwargs, expected_values):
    # Unpack expected properties.
    expected_data, expected_axis_ranges, expected_xlabel, expected_ylabel = expected_values
    # Run plot method.
    output = test_input.plot(**test_kwargs)
    # Check plot properties are correct.
    assert type(output) is LineAnimator
    np.testing.assert_array_equal(output.data, expected_data)
    for i, output_axis_range in enumerate(output.axis_ranges):
        if expected_axis_ranges[i] is not False:
            assert np.allclose(output_axis_range, expected_axis_ranges[i])
    assert output.axes.xaxis.get_label_text() == expected_xlabel
    assert output.axes.yaxis.get_label_text() == expected_ylabel
