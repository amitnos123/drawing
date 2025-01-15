"""
Transmon Qubit Component Module
=============================

This module provides functionality for creating transmon qubit layouts with configurable
corner rounding for both the pads and other features. The implementation supports:
- Independent corner rounding radii for pads and other features
- Optional smoothing for different parts of the transmon
- Configurable junction and pad dimensions
"""

import gdsfactory as gf
import gdsfactory.components as gc
from gdsfactory.typings import LayerSpec
from ..shared import merge_decorator, smooth_corners, DEFAULT_LAYER


@merge_decorator
@gf.cell
def _draw_transmon_with_sharp_edges(
        pad_width: float = 400,
        pad_height: float = 1000,
        pads_distance: float = 150,
        taper_width: float = 45,
        junction_width: float = 1,
        junction_gap: float = 3.4,
        junction_length: float = 10,
        pad_radius: float = 0,
        layer: LayerSpec = DEFAULT_LAYER,
) -> gf.Component:
    """
    Creates a transmon qubit with optionally rounded pads but sharp features elsewhere.

    Args:
        pad_width: Width of the capacitor pads in microns.
        pad_height: Height of the capacitor pads in microns.
        pads_distance: Separation between capacitor pads in microns.
        taper_width: Width of the taper at pad connection in microns.
        junction_width: Width of the Josephson junction in microns.
        junction_gap: Gap between junction arms in microns.
        junction_length: Length of each junction arm in microns.
        pad_radius: Corner rounding radius for pads (0 for sharp corners) in microns.
        layer: Target GDS layer specification.

    Returns:
        gf.Component: Transmon component with specified pad rounding
    """
    c = gf.Component()

    # Create pad with optional corner rounding
    pad = gc.compass((pad_width, pad_height), layer=layer)
    if pad_radius > 0:
        pad = smooth_corners(pad, radius=pad_radius, layer=layer)

    # Create taper connecting pad to junction
    taper = gc.taper(
        length=pads_distance / 2 - junction_gap / 2 - junction_length,
        width1=taper_width,
        width2=junction_width,
        port_names=("e1", "e2"),
        port_types=("electrical", "electrical"),
        layer=layer,
    )

    # Create junction
    junction = gc.compass((junction_length, junction_width), layer=layer)

    # Assemble left side
    left_pad = c << pad
    left_taper = c << taper
    left_junction = c << junction

    left_taper.connect("e1", left_pad.ports["e3"], allow_width_mismatch=True)
    left_junction.connect("e1", left_taper.ports["e2"], allow_width_mismatch=True)

    # Assemble right side
    right_pad = c << pad
    right_pad.dmovex(pads_distance + pad_width)  # Using dmovex for relative movement

    right_taper = c << taper
    right_junction = c << junction

    right_taper.connect("e1", right_pad.ports["e1"], allow_width_mismatch=True)
    right_junction.connect("e3", right_taper.ports["e2"], allow_width_mismatch=True)

    # Add ports for junction connections
    c.add_port("junction_left_arm", left_junction.ports["e3"])
    c.add_port("junction_right_arm", right_junction.ports["e1"])

    # Add port for antenna
    c.add_port('antenna_connection', right_pad.ports['e3'])

    return c


@gf.cell
def _draw_transmon_smooth_edges(
        pad_width: float = 400,
        pad_height: float = 1000,
        pads_distance: float = 150,
        taper_width: float = 45,
        junction_width: float = 1,
        junction_gap: float = 3.4,
        junction_length: float = 10,
        feature_radius: float = 1.0,
        pad_radius: float = 50.0,
        layer: LayerSpec = DEFAULT_LAYER,
) -> gf.Component:
    """
    Creates a transmon qubit with rounded corners for both pads and other features.

    Args:
        pad_width: Width of the capacitor pads in microns.
        pad_height: Height of the capacitor pads in microns.
        pads_distance: Separation between capacitor pads in microns.
        taper_width: Width of the taper at pad connection in microns.
        junction_width: Width of the Josephson junction in microns.
        junction_gap: Gap between junction arms in microns.
        junction_length: Length of each junction arm in microns.
        feature_radius: Corner rounding radius for features (tapers, junctions) in microns.
        pad_radius: Corner rounding radius for pads in microns.
        layer: Target GDS layer specification.

    Returns:
        gf.Component: Fully smoothed transmon component
    """
    c = gf.Component()

    # Create base transmon with rounded pads
    transmon = _draw_transmon_with_sharp_edges(
        pad_width=pad_width,
        pad_height=pad_height,
        pads_distance=pads_distance,
        taper_width=taper_width,
        junction_width=junction_width,
        junction_gap=junction_gap,
        junction_length=junction_length,
        pad_radius=pad_radius,
        layer=layer,
    )

    # Apply smoothing to all features
    transmon = smooth_corners(transmon, radius=feature_radius, layer=layer)
    ref = c << transmon

    # collecting all ports
    ports = transmon.ports

    # modified_ports
    modified_ports = ('junction_left_arm', 'junction_right_arm')

    # Add junction extensions with matching feature radius
    half_junction = gc.compass((feature_radius, junction_width), layer=layer)

    left_ext = c << half_junction
    left_ext.connect("e1", ref.ports["junction_left_arm"])
    left_ext.dmovex(-feature_radius)

    right_ext = c << half_junction
    right_ext.connect("e3", ref.ports["junction_right_arm"])
    right_ext.dmovex(feature_radius)

    # Add ports for external connections
    c.add_port("junction_left_arm", left_ext.ports["e3"])
    c.add_port("junction_right_arm", right_ext.ports["e1"])

    # Adding back all ports that are missing apart from the modified ports
    for port in ports:
        if port.name not in modified_ports:
            c.add_port(port.name, port)

    return c


@merge_decorator
@gf.cell
def draw_transmon(
        pad_width: float = 400,
        pad_height: float = 1000,
        pads_distance: float = 150,
        taper_width: float = 45,
        junction_width: float = 1,
        junction_gap: float = 3.4,
        junction_length: float = 10,
        smooth_features: bool = True,
        feature_radius: float = 10.0,
        pad_radius: float = 50.0,
        layer: LayerSpec = DEFAULT_LAYER,
) -> gf.Component:
    """
    has three ports:
    left_arm
    right_arm
    short_place
    antena output
    start (e1)


    Creates a transmon qubit with configurable corner rounding for different features.

    This is the main function for creating transmon qubits. It provides options for
    independent corner rounding of pads and other features (tapers, junctions).

    Args:
        pad_width: Width of the capacitor pads in microns.
        pad_height: Height of the capacitor pads in microns.
        pads_distance: Separation between capacitor pads in microns.
        taper_width: Width of the taper at pad connection in microns.
        junction_width: Width of the Josephson junction in microns.
        junction_gap: Gap between junction arms in microns.
        junction_length: Length of each junction arm in microns.
        smooth_features: Whether to apply rounding to features beyond the pads.
        feature_radius: Corner rounding radius for features when smooth_features=True.
        pad_radius: Corner rounding radius for capacitor pads (0 for sharp corners).
        layer: Target GDS layer specification.

    Returns:
        gf.Component: Complete transmon component with specified corner rounding
    """
    if smooth_features and feature_radius > 0:
        transmon = _draw_transmon_smooth_edges(
            pad_width=pad_width,
            pad_height=pad_height,
            pads_distance=pads_distance,
            taper_width=taper_width,
            junction_width=junction_width,
            junction_gap=junction_gap,
            junction_length=junction_length,
            feature_radius=feature_radius,
            pad_radius=pad_radius,
            layer=layer,
        )
    else:
        transmon = _draw_transmon_with_sharp_edges(
            pad_width=pad_width,
            pad_height=pad_height,
            pads_distance=pads_distance,
            taper_width=taper_width,
            junction_width=junction_width,
            junction_gap=junction_gap,
            junction_length=junction_length,
            pad_radius=pad_radius,
            layer=layer,
        )

    return transmon


@merge_decorator
def draw_antenna(
        antenna_length: float,
        antenna_width: float,
        antenna_radius: float,
        layer: LayerSpec = DEFAULT_LAYER
):
    c = gf.Component()

    # Create pad with optional corner rounding
    compass = gc.compass((antenna_length, antenna_width), layer=layer)
    circle = gc.circle(radius=antenna_radius, layer=layer)

    compass_ref = c << compass
    circle_ref = c << circle

    circle_port = gf.Port('circle_port', center=circle_ref.center,
                          layer=layer, width=antenna_width, orientation=180)
    compass_ref.connect("e3", circle_port, allow_type_mismatch=True)

    c.add_port('start', port=compass_ref.ports['e1'])
    return c


@merge_decorator
@gf.cell
def draw_transmon_with_antenna(
        pad_width: float = 400,
        pad_height: float = 1000,
        pads_distance: float = 150,
        taper_width: float = 45,
        junction_width: float = 1,
        junction_gap: float = 3.4,
        junction_length: float = 10,
        smooth_features: bool = True,
        feature_radius: float = 10.0,
        pad_radius: float = 50.0,
        antenna_length: float = 1400,
        antenna_width: float = 100,
        antenna_radius: float = 250,
        layer: LayerSpec = DEFAULT_LAYER) -> gf.Component:
    transmon = draw_transmon(pad_width=pad_width,
                             pad_height=pad_height,
                             pads_distance=pads_distance,
                             taper_width=taper_width,
                             junction_width=junction_width,
                             junction_gap=junction_gap,
                             junction_length=junction_length,
                             smooth_features=smooth_features,
                             feature_radius=feature_radius,
                             pad_radius=pad_radius,
                             layer=layer)

    antenna = draw_antenna(
        antenna_length=antenna_length,
        antenna_width=antenna_width,
        antenna_radius=antenna_radius,
        layer=layer
    )

    c = gf.Component()

    transmon = c << transmon
    antenna = c << antenna

    antenna.connect('start', transmon.ports['antenna_connection'], allow_width_mismatch=True)

    ports = filter(lambda x: x.name != 'antenna_connection', transmon.ports)
    for port in ports:
        c.add_port(port.name, port)
    return c
